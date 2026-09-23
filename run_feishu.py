"""启动飞书机器人（独立于 FastAPI 服务）。

用法:  python run_feishu.py
"""
import sys

# 强制 stdout/stderr 用 UTF-8 输出，且遇到无法编码的字符(如 emoji)时用?
# 替换而非报错崩溃，避免 Windows GBK 控制台打日志时 UnicodeEncodeError。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv()

from app import config, feishu


def main() -> None:
    if not config.has_feishu_config():
        print("错误：尚未在 .env 配置 FEISHU_APP_ID / FEISHU_APP_SECRET")
        return
    feishu.run()


if __name__ == "__main__":
    main()
