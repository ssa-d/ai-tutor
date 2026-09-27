"""SQLite 持久化存储：把对话历史和日志存到数据库文件。

- messages 表：对话历史（长期记忆）
- daily_logs 表：每天的日志记录（用于"每日总结"）

用 Python 自带的 sqlite3，无需额外安装。
数据库文件默认是项目根目录的 ai_tutor.db（在 .gitignore 里忽略）。
"""

import sqlite3
from pathlib import Path

# 数据库文件位置（项目根目录）
DB_PATH = Path(__file__).resolve().parent.parent / "ai_tutor.db"


def _connect() -> sqlite3.Connection:
    """建立数据库连接，并确保所有表存在。"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
        """
    )
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


# ---------------------------------------------------------------------------
# 对话历史（长期记忆）
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# 日志（记录每天干了什么，供每日总结）
# ---------------------------------------------------------------------------


def save_log(chat_id: str, content: str) -> None:
    """往日志表写一条记录（记录今天干了什么）。"""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO daily_logs (chat_id, content) VALUES (?, ?)",
            (chat_id, content),
        )
        conn.commit()


def load_today_logs(chat_id: str) -> list[dict]:
    """查出"今天"这个会话的所有日志，按时间正序返回。

    返回:
        形如 [{"content": "...", "created_at": "2026-09-25 20:00:00"}, ...] 的列表。
    """
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT content, created_at FROM daily_logs
            WHERE chat_id = ? AND DATE(created_at) = DATE('now', 'localtime')
            ORDER BY id ASC
            """,
            (chat_id,),
        ).fetchall()
    return [{"content": r[0], "created_at": r[1]} for r in rows]


def clear_logs(chat_id: str) -> None:
    """清空某个会话的所有日志。"""
    with _connect() as conn:
        conn.execute("DELETE FROM daily_logs WHERE chat_id = ?", (chat_id,))
        conn.commit()


if __name__ == "__main__":
    # 自测：对话历史 + 日志
    test_chat = "__test__"
    save_message(test_chat, "user", "你好")
    save_message(test_chat, "assistant", "你好呀")
    print("历史:", load_history(test_chat))
    clear_history(test_chat)

    save_log(test_chat, "写了 Python 作业")
    save_log(test_chat, "跑了 3 公里")
    print("今天的日志:", load_today_logs(test_chat))
    clear_logs(test_chat)
    print("清空日志后:", load_today_logs(test_chat))
