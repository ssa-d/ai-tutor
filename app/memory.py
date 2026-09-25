"""对话记忆模块。

负责维护和管理 AI Tutor 的多轮对话历史。
- summarize_messages(): 把历史压缩成一行摘要（工具函数）
- ChatMemory: 一个"类"，管理某个用户会话的记忆（可保存/读取/裁剪/清空）

第 3 课预习：用「类(class)」来封装"数据 + 操作数据的方法"，每个用户一个实例。
"""


class ChatMemory:
    """管理一段多轮对话记忆。

    每个实例代表一个用户会话的"记忆盒子"，各自有独立的 history。
    通过 add_user / add_assistant 不断追加，get_messages 取出完整历史，
    交给 llm.chat() 即可让 AI 记住上下文。
    """

    def __init__(self, max_len: int = 20):
        """创建记忆盒子。max_len 是历史最多保留多少条（超出裁剪）。"""
        self.history: list[dict] = []   # 对话历史，每个元素是 {"role","content"}
        self.max_len = max_len          # 允许的最长历史条数

    def add_user(self, text: str) -> None:
        """记录用户说的一句话。"""
        self.history.append({"role": "user", "content": text})
        self._trim()

    def add_assistant(self, text: str) -> None:
        """记录 AI 回答的一句话。"""
        self.history.append({"role": "assistant", "content": text})
        self._trim()

    def get_messages(self) -> list[dict]:
        """返回完整对话历史（一个列表，可直接传给 llm.chat）。"""
        return self.history

    def clear(self) -> None:
        """清空这段记忆。"""
        self.history = []

    def _trim(self) -> None:
        """历史超过 max_len 条时，丢掉最旧的消息，防止无限增长。"""
        if len(self.history) > self.max_len:
            # 只保留末尾 max_len 条
            self.history = self.history[-self.max_len:]


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
    mem = ChatMemory()
    mem.add_user("我叫小明")
    mem.add_assistant("你好小明！")
    mem.add_user("我叫什么名字？")
    print(summarize_messages(mem.get_messages()))

    demo = [
        {"role": "user", "content": "什么是 Python？"},
        {"role": "assistant", "content": "Python 是一种编程语言。"},
        {"role": "user", "content": "什么是列表推导式？"},
    ]
    print(summarize_messages(demo))
