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

def chat(messages: list[dict], system_prompt: str = "你是一个乐于助人的 AI 学习助手。") -> str:
    """向 DeepSeek 发送完整的多轮对话（带记忆），返回回答。

    参数:
        messages: 完整对话历史，每个元素形如 {"role": "...", "content": "..."}。
                  调用前请把前面所有 user 句和 assistant 句都 append 进来，
                  这样模型才能"记住"之前聊过什么。
        system_prompt: 可选的系统提示词（AI 的人设），默认是学习助手。

    返回:
        模型生成的回答文本。
    """
    # 在用户传来的历史最前头，加一条"人设"消息
    full = [
        {"role": "system", "content": system_prompt},
    ] + messages

    response = _client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=full,
    )
    return response.choices[0].message.content.strip()
