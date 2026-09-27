"""查看 SQLite 数据库里的长期记忆（对话历史 + 日志）。

用法:
    python view_memory.py            # 查看所有
    python view_memory.py 10         # 只查最近 10 条
"""
import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path(__file__).resolve().parent / "ai_tutor.db"

n = 20
if len(sys.argv) > 1:
    try:
        n = int(sys.argv[1])
    except ValueError:
        pass


def _columns(conn, table):
    """返回某张表的所有列名。"""
    return [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')]


def main():
    if not DB.exists():
        print(f"数据库不存在：{DB}")
        return

    conn = sqlite3.connect(DB)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'") if not r[0].startswith("sqlite_")]
    print(f"数据库：{DB}")
    print(f"表：{tables}  （显示每张表最近 {n} 条）")
    print("=" * 70)

    for t in tables:
        cols = _columns(conn, t)
        cnt = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"\n📄 表 [{t}]：共 {cnt} 条记录  列={cols}")

        # 根据表结构选择要显示的列
        if "content" in cols:
            rows = conn.execute(f'SELECT * FROM "{t}" ORDER BY rowid DESC LIMIT ?', (n,)).fetchall()
            for r in rows:
                # 把每一列凑成 "列名=值"，content 显示前 60 字
                parts = []
                for col, val in zip(cols, r):
                    if col == "content":
                        parts.append(f"content={str(val)[:60]}")
                    else:
                        parts.append(f"{col}={val}")
                print("  " + "  ".join(parts))
        else:
            print("  （该表无 content 列，跳过）")
    conn.close()


if __name__ == "__main__":
    main()
