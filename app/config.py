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
