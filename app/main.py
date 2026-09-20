"""FastAPI 应用：定义路由（Web 接口）。

- GET  /             返回聊天网页界面
- GET  /health       健康检查
- POST /api/chat     接收用户提问，调用 DeepSeek 回答（JSON API）
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import config, llm

# 前端静态文件目录（存放 index.html）
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI Tutor",
    description="一个用 DeepSeek 驱动的 AI 学习助手",
    version="0.1.0",
)


# ---------------------------------------------------------------------------
# 请求 / 响应数据模型
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    """客户端发送到 /api/chat 的请求体。"""

    message: str                      # 用户输入的问题
    system_prompt: str = "你是一个乐于助人的 AI 学习助手。"  # 可选的系统提示词


class ChatResponse(BaseModel):
    """服务端返回给客户端的响应体。"""

    reply: str   # AI 的回答


# ---------------------------------------------------------------------------
# 路由
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def root():
    """首页：返回聊天网页界面。"""
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "AI Tutor 服务已启动。static/index.html 未找到。"}


@app.get("/health")
def health():
    """健康检查：让外部知道服务是否存活。"""
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """处理用户提问，返回 DeepSeek 的回答。"""
    # 如果没配置 API Key，给出友好错误
    if not config.has_api_key():
        raise HTTPException(
            status_code=500,
            detail="服务端尚未配置 DEEPSEEK_API_KEY，请在 .env 中填写后重启服务。",
        )

    question = req.message.strip()
    if not question:
        raise HTTPException(status_code=422, detail="message 不能为空。")

    try:
        reply = llm.ask(question, req.system_prompt)
    except Exception as exc:  # 调用大模型出错时给出清晰提示
        raise HTTPException(status_code=502, detail=f"调用 DeepSeek 失败：{exc}")

    return ChatResponse(reply=reply)
