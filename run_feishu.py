"""启动飞书机器人（独立于 FastAPI 服务）。

用法:  python run_feishu.py
"""
import os
import sys

# 强制 stdout/stderr 用 UTF-8 输出，遇到 emoji 等用?替换而非崩溃，
# 避免 Windows GBK 控制台打日志时 UnicodeEncodeError。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# 让飞书机器人"稳定直连"，不读系统代理。
#
# 背景：部分网络环境下系统会配一个代理(如 127.0.0.1:65532)，若该代理软件
# 未运行，requests 会因 ProxyError 连不上飞书。这里给 requests 全局补丁，
# 强制 trust_env=False，让它完全不读系统代理，走直连。这样系统代理开不开
# 都不影响飞书机器人。
# ---------------------------------------------------------------------------
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"
try:
    import requests
    import requests.sessions
    _requests_original_request = requests.sessions.Session.request

    def _requests_no_proxy(self, *args, **kwargs):
        self.trust_env = False          # 忽略系统代理/环境代理
        return _requests_original_request(self, *args, **kwargs)

    requests.sessions.Session.request = _requests_no_proxy
except Exception as e:  # 补丁失败不影响启动，只是可能又走代理
    print(f"[警告] 代理禁用补丁未生效: {e}")

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
