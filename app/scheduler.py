"""定时主动推送模块。

让机器人"主动"在固定时间给用户发消息，例如：
- 每天 21:00 提醒记录今天干了啥
- 每天 22:00 自动整理并发送今天的日志总结

实现原理（多线程）：
- run_feishu.py 主线程跑 WebSocket（收消息）
- 本模块在一个独立线程里跑 schedule 循环（到点执行任务）
两个"一直在跑"的任务互不干扰。
"""

import threading
import time

import schedule

from . import config, feishu, llm, storage


def _remind_to_log() -> None:
    """到点提醒：主动发消息，请用户记录今天。"""
    text = "🕘 该记一下今天啦！可以跟我说说今天都干了啥，我帮你记进日志～\n（或说「总结今天」看看今天的日报）"
    feishu.send_active_message(config.FEISHU_TARGET_CHAT_ID, text)


def _send_daily_summary() -> None:
    """到点自动发"今日总结"日报。"""
    chat_id = config.FEISHU_TARGET_CHAT_ID
    logs = storage.load_today_logs(chat_id)
    if not logs:
        feishu.send_active_message(chat_id, "📭 今天还没有记录哦，暂时没有日报～")
        return
    lines = "\n".join(f"- {log['created_at']} {log['content']}" for log in logs)
    prompt = (
        "下面是我今天的活动记录，请整理成一段自然流畅的中文'今日总结'日报，"
        "语气友好、有条理，不要编造：\n\n" + lines
    )
    reply = llm.chat(
        [{"role": "user", "content": prompt}],
        system_prompt="你是一名贴心的个人助理，帮我整理每日总结。",
    )
    feishu.send_active_message(chat_id, "📋 今日总结（自动推送）：\n\n" + reply)


def _setup_jobs() -> None:
    """注册定时任务。"""
    if config.REMINDER_TIME:
        schedule.every().day.at(config.REMINDER_TIME).do(_remind_to_log)
        print(f"[定时] 每天 {config.REMINDER_TIME} 提醒记录日志")
    if config.SUMMARY_TIME:
        schedule.every().day.at(config.SUMMARY_TIME).do(_send_daily_summary)
        print(f"[定时] 每天 {config.SUMMARY_TIME} 自动发送今日总结")


def start() -> None:
    """在一个独立线程里启动定时任务循环（非阻塞，直接返回）。"""
    _setup_jobs()

    def _loop():
        print("[定时] 定时任务线程已启动")
        while True:
            schedule.run_pending()
            time.sleep(1)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()