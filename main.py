"""程序入口：加载环境变量并启动 FastAPI 服务。

直接运行：python main.py
"""
import os

from dotenv import load_dotenv
import uvicorn

# 加载 .env 文件里的配置（如 API Key）
load_dotenv()


if __name__ == "__main__":
    # host 0.0.0.0 允许局域网访问；reload 开启代码热重载方便开发
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
