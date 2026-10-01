"""飞书机器人接入模块。

通过飞书官方 SDK（lark-oapi）的 WebSocket 长连接模式接收用户的私聊消息，
用 ChatMemory 记住多轮上下文，再调用 DeepSeek（llm.chat）生成回答。

日志功能（方案 A+）：
- 明确指令（"记录：xxx" / "总结今天"）直接处理
- 自然语句：用 DeepSeek 判断是否"想记录今天干了啥"，若是则反问确认，
  用户回"好"才真正存日志（避免闲聊弄脏日志）

特点：
- WebSocket 长连接：无需公网 IP / 内网穿透
- 多轮记忆 + 长期记忆（SQLite）
- 依赖 .env 里的 FEISHU_APP_ID / FEISHU_APP_SECRET
"""

import json
import traceback

from lark_oapi import Client as LarkClient
from lark_oapi import EventDispatcherHandler, LogLevel
from lark_oapi.api.im.v1 import ReplyMessageRequest, ReplyMessageRequestBody
from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody
from lark_oapi.ws import Client as WsClient

from . import config, llm, storage
from .memory import ChatMemory


# 全局会话记忆：chat_id -> ChatMemory
_sessions: dict[str, ChatMemory] = {}

# "待确认"的日志：chat_id -> 准备记录的内容
# 例如机器人反问"要记录吗"之后，在用户回复"好"之前，先存在这里
_pending_logs: dict[str, str] = {}

# 确认关键词集合：用户说这些就代表"要记录"
_YES_WORDS = {"好", "嗯", "要", "记", "记得", "是的", "可以", "对", "ok", "okay", "行", "要的", "要记", "记下"}
# 取消关键词集合：用户说这些代表"不记录"
_NO_WORDS = {"不用", "不要", "算了", "不", "别", "no", "算了把", "不需要", "不是"}


def _get_session(chat_id: str) -> ChatMemory:
    """取出某个会话的记忆盒子；没有就新建一个。"""
    mem = _sessions.get(chat_id)
    if mem is None:
        mem = ChatMemory(chat_id=chat_id)   # 从数据库加载历史
        _sessions[chat_id] = mem
    return mem


def _handle_confirmation(chat_id: str, text: str) -> str | None:
    """处理"待确认"状态：用户回应"好 / 不用"。

    返回:
        若这是一次针对待确认日志的回复，返回要发给用户的文本；
        否则返回 None（继续当普通消息处理）。
    """
    pending = _pending_logs.get(chat_id)
    if pending is None:
        # 没有待确认的东西，不是确认回复
        return None

    t = text.strip()
    # 命中了"要记录"的关键词 -> 真的存日志
    if t in _YES_WORDS or t.startswith("好") or t.startswith("要"):
        _pending_logs.pop(chat_id, None)
        storage.save_log(chat_id, pending)
        return f"✅ 已记下：{pending}"

    # 命中了"不记录"的关键词 -> 取消
    if t in _NO_WORDS or t.startswith("不") or t.startswith("算"):
        _pending_logs.pop(chat_id, None)
        return "好，那这条我就不记啦～"

    # 用户回的是别的话：不改变待确认状态，交给普通对话处理（返回 None）
    return None


def _classify_intent(text: str) -> str:
    """用 DeepSeek 判断这句话是不是"想记录今天干了啥"。

    返回:
        "record"（想记录）或 "chat"（普通聊天）。
    """
    prompt = (
        "判断这句话的意图，只回答一个词 record 或 chat：\n"
        "- record：用户正在分享/记录自己今天做了什么、去了哪、发生了什么、心情等日常活动\n"
        "- chat：普通的闲聊、提问、求助、打招呼\n\n"
        f"句子：{text}"
    )
    try:
        ans = llm.chat(
            [{"role": "user", "content": prompt}],
            system_prompt="你是意图分类器，只输出 record 或 chat 这一个英文单词，不要输出多余内容。",
        )
        ans = (ans or "").strip().lower()
        return "record" if "record" in ans else "chat"
    except Exception as exc:
        print(f"[WARN] 意图分类失败，按普通聊天处理: {exc}")
        return "chat"


def _handle_log_command(chat_id: str, text: str) -> str | None:
    """识别并处理日志相关的指令/意图（方案 A+）。

    返回:
        若要转入日志流程，返回要发给用户的回复文本；
        若不是日志相关，返回 None（走普通对话）。
    """
    # --- 1) 明确记录指令：'我今天干了xxx' / '记录：xxx' ---
    if text.startswith("我今天干了") or text.startswith("记录"):
        if text.startswith("我今天干了"):
            log_content = text[len("我今天干了"):].strip(" ：：:") or text
        else:
            log_content = text[len("记录"):].strip(" ：:") or text
        storage.save_log(chat_id, log_content)
        return f"✅ 已记下：{log_content}"

    # --- 2) 明确总结指令：'总结今天' / '总结一下今天' ---
    if ("总结" in text and "今天" in text) or text.strip() in {"总结", "日报"}:
        logs = storage.load_today_logs(chat_id)
        if not logs:
            return "📭 今天还没有记录哦。可以告诉我你今天做了啥，我会帮你记下来～"
        lines = "\n".join(f"- {log['created_at']} {log['content']}" for log in logs)
        prompt = (
            "下面是我今天的活动记录，请把它们整理成一段自然流畅的中文'今日总结'日报，"
            "语气友好、有条理，不要编造没有的内容：\n\n" + lines
        )
        reply = llm.chat(
            [{"role": "user", "content": prompt}],
            system_prompt="你是一名贴心的个人助理，帮我整理每日总结。",
        )
        return "📋 今日总结：\n\n" + reply

    # --- 3) 自然语句：用 DeepSeek 判断是不是"想记录" ---
    # 只有这句话不像明确的闲聊时才判断（这里统一判断一次，成本可控）
    intent = _classify_intent(text)
    if intent == "record":
        # 反问确认，先存进 pending，等用户说"好"再真记录
        _pending_logs[chat_id] = text
        return f"🗒 我理解你在记录今天的活动～ 要我把这句记进今天的日志吗？\n「{text}」\n（回「好」我就记，回「不用」就跳过）"

    # --- 4) 其他：交给普通对话 ---
    return None


def _build_event_handler():
    """构建 WebSocket 事件分发器，并注册"收到消息"事件。"""
    return (
        EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(_on_message_received)
        .build()
    )


def _on_message_received(data) -> None:
    """处理收到的飞书消息的角色入口。"""
    print("[DEBUG] 收到一个事件回调")
    try:
        event = data.event
        message = event.message
        if message.message_type != "text":
            print("[DEBUG] 非文本消息，忽略")
            return

        content = json.loads(message.content)
        text = (content.get("text") or "").strip()
        if not text:
            return
        chat_id = message.chat_id
        msg_id = message.message_id
        mem = _get_session(chat_id)

        # ---- 第 0 步：先处理"待确认日志"的回复（好/不用）----
        confirm_reply = _handle_confirmation(chat_id, text)
        if confirm_reply is not None:
            _reply_message(msg_id, confirm_reply)
            print(f"[DEBUG] 处理了确认回复: {confirm_reply}")
            return

        # ---- 第 1 步：处理日志指令/意图 ----
        log_reply = _handle_log_command(chat_id, text)
        if log_reply is not None:
            _reply_message(msg_id, log_reply)
            print(f"[DEBUG] 按日志流程处理: {log_reply[:40]}...")
            return

        # ---- 第 2 步：普通多轮对话 ----
        mem.add_user(text)
        reply = llm.chat(mem.get_messages())
        mem.add_assistant(reply)
        _reply_message(msg_id, reply)
        print("[DEBUG] 已发送普通回复")
    except Exception as exc:
        print("[ERROR] 处理消息异常：")
        traceback.print_exc()
        try:
            _reply_message(data.event.message.message_id, f"(处理出错，请稍后再试：{exc})")
        except Exception:
            pass


def _reply_message(message_id: str, reply: str) -> None:
    """通过 IM API 回复一条消息。"""
    request = (
        ReplyMessageRequest.builder()
        .message_id(message_id)
        .request_body(
            ReplyMessageRequestBody.builder()
            .msg_type("text")
            .content(json.dumps({"text": reply}))
            .build()
        )
        .build()
    )
    im_client.im.v1.message.reply(request)


# ---------------------------------------------------------------------------
# 初始化客户端
# ---------------------------------------------------------------------------
im_client = LarkClient.builder().app_id(config.FEISHU_APP_ID).app_secret(config.FEISHU_APP_SECRET).log_level(LogLevel.INFO).build()
ws_client = WsClient(
    app_id=config.FEISHU_APP_ID,
    app_secret=config.FEISHU_APP_SECRET,
    log_level=LogLevel.INFO,
    event_handler=_build_event_handler(),
)



def send_active_message(chat_id: str, text: str) -> bool:
    """主动给某个会话发一条文本消息（不依赖用户先发消息）。

    用于定时推送/主动提醒。返回是否发送成功。
    """
    try:
        request = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("text")
                .content(json.dumps({"text": text}))
                .build()
            )
            .build()
        )
        resp = im_client.im.v1.message.create(request)
        ok = resp.code == 0
        print(f"[PUSH] 主动发消息{'成功' if ok else '失败'} code={resp.code} msg={resp.msg}")
        return ok
    except Exception as exc:
        print(f"[PUSH] 主动发消息异常: {exc}")
        return False
def run() -> None:
    """启动飞书机器人（阻塞式长连接，一直运行）。"""
    print("飞书机器人已启动，等待消息……")
    ws_client.start()
