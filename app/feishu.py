"""飞书机器人接入模块。

通过飞书官方 SDK（lark-oapi）的 WebSocket 长连接模式接收用户的私聊消息，
用 ChatMemory 为每个用户会话记住历史，再调用 DeepSeek（llm.chat）生成回答，
最后通过 IM API 回复用户。

特点：
- WebSocket 长连接：无需公网 IP / 内网穿透，最适合个人开发
- 多轮记忆：每个会话(chat_id)有独立的 ChatMemory，AI 能记住上下文
- 依赖 .env 里的 FEISHU_APP_ID / FEISHU_APP_SECRET
"""

import json
import traceback

from lark_oapi import Client as LarkClient
from lark_oapi import EventDispatcherHandler, LogLevel
from lark_oapi.api.im.v1 import ReplyMessageRequest, ReplyMessageRequestBody
from lark_oapi.ws import Client as WsClient

from . import config, llm
from .memory import ChatMemory


# 全局会话记忆：chat_id -> ChatMemory（每个用户一个记忆盒子，互不干扰）
_sessions: dict[str, ChatMemory] = {}


def _get_session(chat_id: str) -> ChatMemory:
    """取出某个会话的记忆盒子；没有就新建一个。"""
    mem = _sessions.get(chat_id)
    if mem is None:
        mem = ChatMemory()          # 新会话：从零开始记忆
        _sessions[chat_id] = mem
    return mem


def _build_event_handler():
    """构建 WebSocket 事件分发器，并注册"收到消息"事件。"""
    return (
        EventDispatcherHandler.builder("", "")  # 未开启加密/签名校验，传空串
        .register_p2_im_message_receive_v1(_on_message_received)
        .build()
    )


def _on_message_received(data) -> None:
    """处理收到的飞书消息：解析 -> 存记忆 -> 调 DeepSeek -> 存回答 -> 回复。（含调试日志）"""
    print("[DEBUG] 收到一个事件回调")
    try:
        event = data.event
        message = event.message
        print(f"[DEBUG] message_type={message.message_type} content={message.content}")
        print(f"[DEBUG] chat_id={message.chat_id} message_id={message.message_id}")

        # 只处理文本消息；图片、文件等先忽略
        if message.message_type != "text":
            print("[DEBUG] 非文本消息，忽略")
            return

        # content 是 JSON 字符串，例如 {"text": "你好"}
        content = json.loads(message.content)
        text = (content.get("text") or "").strip()
        print(f"[DEBUG] 提取到文本: {text}")
        if not text:
            print("[DEBUG] 文本为空，忽略")
            return

        # 1) 取出这个会话的记忆盒子
        chat_id = message.chat_id
        mem = _get_session(chat_id)

        # 2) 记住用户说的话
        mem.add_user(text)
        print(f"[DEBUG] 当前记忆条数: {len(mem.get_messages())}")

        # 3) 用完整历史生成 AI 回答（带记忆）
        print("[DEBUG] 正在调用 DeepSeek（带记忆）……")
        reply = llm.chat(mem.get_messages())
        print(f"[DEBUG] 得到回答: {str(reply)[:50]}...")

        # 4) 记住 AI 的回答
        mem.add_assistant(reply)

        # 5) 回复用户
        _reply_message(message.message_id, reply)
        print("[DEBUG] 已发送回复")
    except Exception as exc:
        print("[ERROR] 处理消息异常：")
        traceback.print_exc()
        try:
            msg_id = data.event.message.message_id
            _reply_message(msg_id, f"(处理出错，请稍后再试：{exc})")
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
# 初始化客户端（模块导入时仅定义，启动时才真正连接）
# ---------------------------------------------------------------------------

# 用来"回复消息"的普通 Lark 客户端
im_client = LarkClient.builder().app_id(config.FEISHU_APP_ID).app_secret(config.FEISHU_APP_SECRET).log_level(LogLevel.INFO).build()

# 用来"接收消息"的 WebSocket 长连接客户端
ws_client = WsClient(
    app_id=config.FEISHU_APP_ID,
    app_secret=config.FEISHU_APP_SECRET,
    log_level=LogLevel.INFO,
    event_handler=_build_event_handler(),
)


def run() -> None:
    """启动飞书机器人（阻塞式长连接，一直运行）。"""
    print("飞书机器人已启动，等待消息……")
    ws_client.start()
