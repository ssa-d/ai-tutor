"""对话记忆模块。

负责维护和管理 AI Tutor 的多轮对话历史。
- summarize_messages(): 把历史压缩成一行摘要（工具函数）
- ChatMemory: 管理某个用户会话的记忆，可持久化到 SQLite（长期记忆）

第 3 课：用「类(class)」封装"数据 + 操作数据的方法"，每个用户一个实例。
"""

from . import storage


class ChatMemory:
    """管理一段多轮对话记忆（可持久化到 SQLite）。

    每个实例代表一个用户会话的"记忆盒子"。
    - 如果给了 chat_id，会自动从数据库加载该会话的历史（实现"重启后还记得"）。
    - add_user / add_assistant 追加消息，同时写入数据库。
    - get_messages 取出完整历史，交给 llm.chat()。
    """

    def __init__(self, chat_id: str = "", max_len: int = 20, persist: bool = True):
        """创建记忆盒子。

        参数:
            chat_id: 会话 ID（如飞书 chat_id）。用于按会话隔离 + 持久化。
            max_len: 历史最多保留多少条（超出裁剪）。这里裁剪仅针对本次读取，持久化仍保留全部。
            persist: 是否持久化到 SQLite（True=长期记忆，False=仅内存/临时）。
        """
        self.chat_id = chat_id
        self.max_len = max_len
        self.persist = persist
        # 从数据库加载历史（若有）
        self.history: list[dict] = storage.load_history(chat_id) if persist and chat_id else []

    def add_user(self, text: str) -> None:
        """记录用户说的一句话。"""
        self.history.append({"role": "user", "content": text})
        self._save("user", text)

    def add_assistant(self, text: str) -> None:
        """记录 AI 回答的一句话。"""
        self.history.append({"role": "assistant", "content": text})
        self._save("assistant", text)

    def get_messages(self) -> list[dict]:
        """返回完整对话历史（限制在 max_len 条，避免上下文过长）。"""
        if len(self.history) > self.max_len:
            return self.history[-self.max_len:]
        return self.history

    def clear(self) -> None:
        """清空当前会话的记忆（内存 + 数据库）。"""
        if self.persist and self.chat_id:
            storage.clear_history(self.chat_id)
        self.history = []

    def _save(self, role: str, content: str) -> None:
        """把一条消息写入数据库（若开启持久化且有 chat_id）。"""
        if self.persist and self.chat_id:
            storage.save_message(self.chat_id, role, content)


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
    parts: list[str] = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        parts.append(f"{role}:{content}")
    return " | ".join(parts)


if __name__ == "__main__":
    # 自测：带 chat_id 的持久化记忆
    test_mem = ChatMemory(chat_id="__selftest__", max_len=10)
    test_mem.clear()                    # 先清干净
    test_mem.add_user("我叫小满")
    test_mem.add_assistant("你好小满！")

    # 模拟"重启"：重新创建一个实例，看能否从数据库加载回历史
    mem_after_restart = ChatMemory(chat_id="__selftest__", max_len=10)
    print("重启后加载到的历史:", summarize_messages(mem_after_restart.get_messages()))
    test_mem.clear()
