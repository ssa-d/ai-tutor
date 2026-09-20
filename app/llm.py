"""封装对 DeepSeek 大模型的调用。

通过 OpenAI 兼容的 SDK（openai 库）调用 DeepSeek 的聊天接口。
对外只暴露一个 ask() 函数，调用方无需关心底层细节。
"""
from openai import OpenAI

from . import config

# 初始化客户端：DeepSeek 使用 OpenAI 兼容协议，所以复用 openai 库
_client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)


def ask(question: str, system_prompt: str = "你是一个乐于助人的 AI 学习助手。") -> str:
    """向 DeepSeek 提问并返回回答文本。

    参数:
        question: 用户的问题。
        system_prompt: 系统提示词，可自定义 AI 的角色。

    返回:
        模型生成的回答文本（去除了首尾空白）。
    """
    response = _client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    # 取出第一条返回内容
    return response.choices[0].message.content.strip()
