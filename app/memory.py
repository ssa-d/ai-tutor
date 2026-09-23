"""对话记忆模块。

负责维护和管理 AI Tutor 的多轮对话历史。
目前包含一个工具函数 summarize_messages()，后续会扩展为
更完整的 ChatMemory 类（第 3 课将实现），用于保存、读取、清理对话。

第 1 课练习：编写把多轮消息压缩成一行摘要的函数。
"""


def summarize_messages(messages: list[dict]) -> str:
    """把多轮对话消息压缩成一行可读的摘要。

    参数:
        messages: 消息列表，每个元素是形如
            {"role": "user", "content": "xxx"} 的字典。

    返回:
        一行摘要，每个消息变成 "role:content"，用 " | " 连接。

    示例:
        >>> summarize_messages([
        ...     {"role": "user", "content": "你好"},
        ...     {"role": "assistant", "content": "你好呀"},
        ... ])
        'user:你好 | assistant:你好呀'
    """
    parts: list[str] = []            # 用来装每个 "role:content" 片段
    for msg in messages:             # 遍历每一条消息字典
        role = msg["role"]
        content = msg["content"]
        parts.append(f"{role}:{content}")   # 拼成 "user:你好" 这样的片段
    return " | ".join(parts)         # 用 " | " 把所有片段连成一行


if __name__ == "__main__":
    # 直接运行 python app/memory.py 时，做个简单自测
    demo = [
        {"role": "user", "content": "什么是 Python？"},
        {"role": "assistant", "content": "Python 是一种编程语言。"},
        {"role": "user", "content": "什么是列表推导式？"},
    ]
    print(summarize_messages(demo))
