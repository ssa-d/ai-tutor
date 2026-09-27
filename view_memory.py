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

# 默认查最近 20 条，也允许命令行传数字
n = 20
if len(sys.argv) > 1:
    try:
        n = int(sys.argv[1])
    except ValueError:
        pass


def main():
    if not DB.exists():
        print(f"数据库不存在：{DB}")
        print("请先启动飞书机器人和 AI 聊几句，数据会存到这里。")
        return

    conn = sqlite3.connect(DB)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    print(f"数据库：{DB}")
    print(f"表：{tables}")
    print(f"（显示最近 {n} 条）")
    print("=" * 70)

    for t in tables:
        if t.startswith("sqlite_"):
            continue
        cnt = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"\n📄 表 [{t}]：共 {cnt} 条记录")
        try:
            rows = conn.execute(
                f'SELECT id, chat_id, role, content, created_at FROM "{t}" ORDER BY id DESC LIMIT ?',
                (n,),
            ).fetchall()
            for r in rows:
                print(f"  #{r[0]} [{r[4]}] chat={r[1][:12]}... role={r[2]}: {str(r[3])[:60]}")
        except Exception as e:
            print(f"  读取失败: {e}")
    conn.close()


if __name__ == "__main__":
    main()
