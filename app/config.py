"""读取项目配置（环境变量）。

本文件负责从环境变量（通常来自 .env 文件）读取配置，
例如 DeepSeek API Key 和模型名称。
"""
import os

# ---------------------------------------------------------------------------
# 配置项
# ---------------------------------------------------------------------------

# DeepSeek API Key：从环境变量读取，没有则给一个空字符串并给出提示
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")

# 模型名称
DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# DeepSeek 的接口地址（openai 兼容）
DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"


def has_api_key() -> bool:
    """是否已配置 API Key。"""
    return bool(DEEPSEEK_API_KEY.strip())


# ---------------------------------------------------------------------------
# 飞书机器人配置
# ---------------------------------------------------------------------------

# 飞书应用凭证（到飞书开放平台「凭证与基础信息」获取，敏感信息只放 .env）
FEISHU_APP_ID: str = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET: str = os.getenv("FEISHU_APP_SECRET", "")


def has_feishu_config() -> bool:
    """是否已配置飞书应用凭证。"""
    return bool(FEISHU_APP_ID.strip() and FEISHU_APP_SECRET.strip())


# ---------------------------------------------------------------------------
# 主动推送 / 定时提醒配置
# ---------------------------------------------------------------------------

# 主动发消息的目标会话 ID（你自己的飞书私聊 chat_id）
FEISHU_TARGET_CHAT_ID: str = os.getenv("FEISHU_TARGET_CHAT_ID", "oc_df8824d48220fb34efa7bc8acd5dd1df")

# 每天提醒"记录今天"的时间（24小时制 HH:MM）
REMINDER_TIME: str = os.getenv("REMINDER_TIME", "21:00")

# 每天自动发"今日总结"日报的时间（24小时制，空串=不自动发日报）
SUMMARY_TIME: str = os.getenv("SUMMARY_TIME", "22:00")
