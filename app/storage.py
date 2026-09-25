"""SQLite 持久化存储：把对话历史存到数据库文件。

为什么需要：
- 现在的 ChatMemory 把历史存在"内存"里，重启机器人就清空。
- 存到 SQLite 后，即使机器人重启，记忆也能保留下来（长期记忆）。

用 Python 自带的 sqlite3，无需额外安装。
数据库文件默认是项目根目录的 ai_tutor.db（在 .gitignore 里忽略）。
"""

import sqlite3
from pathlib import Path

# 数据库文件位置（项目根目录）
DB_PATH = Path(__file__).resolve().parent.parent / "ai_tutor.db"


def _connect() -> sqlite3.Connection:
    """建立数据库连接，并确保表存在。"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,          -- user / assistant / system
            content TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
        """
    )
    conn.commit()
    return conn


def save_message(chat_id: str, role: str, content: str) -> None:
    """往数据库写一条消息。"""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content),
        )
        conn.commit()


def load_history(chat_id: str, limit: int = 50) -> list[dict]:
    """读取某个会话最近的历史（最多 limit 条，按时间正序返回）。

    返回:
        形如 [{"role": "user", "content": "..."}, ...] 的列表，可直接传给 llm.chat()。
    """
    with _connect() as conn:
        # 先取末尾 limit 条（id 降序），再整体反转成时间正序
        rows = conn.execute(
            """
            SELECT role, content FROM (
                SELECT role, content, id FROM messages
                WHERE chat_id = ?
                ORDER BY id DESC
                LIMIT ?
            ) ORDER BY id ASC
            """,
            (chat_id, limit),
        ).fetchall()
    return [{"role": r[0], "content": r[1]} for r in rows]


def clear_history(chat_id: str) -> None:
    """清空某个会话的所有历史。"""
    with _connect() as conn:
        conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        conn.commit()


if __name__ == "__main__":
    # 自测：写一条、读出来、清空
    test_chat = "__test__"
    save_message(test_chat, "user", "你好")
    save_message(test_chat, "assistant", "你好呀")
    print("历史:", load_history(test_chat))
    clear_history(test_chat)
    print("清空后:", load_history(test_chat))
