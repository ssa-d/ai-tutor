# AI Tutor — AI 智能学习助手

> 一个使用 **FastAPI + DeepSeek 大模型** 搭建的 AI 学习助手 Web API。
> 这是你的长期 Python 学习项目（GitHub 作品集）的 **阶段 1：最小可运行示例**。

---

## 项目简介

AI Tutor 是一个带 Web 接口的 AI 助手：
- 启动后，访问 `http://127.0.0.1:8000` 即可看到服务信息；
- 向 `/api/chat` 发送一条消息，就能收到 DeepSeek 大模型的回答；
- 自带交互式接口文档，方便测试与调试。

**为什么选这个题目？** 它把"Web 开发、调用大模型 API、环境配置"这些技能融合在一起，是你作为智能科学与技术专业学生既感兴趣、又能持续升级 Python 能力的方向。

---

## 技术栈

| 组件 | 作用 |
|------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | 现代 Python Web 框架，自带交互式 API 文档 |
| [Uvicorn](https://www.uvicorn.org/) | ASGI 服务器，用来运行 FastAPI |
| [openai](https://github.com/openai/openai-python) | DeepSeek 官方推荐的 OpenAI 兼容 SDK |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 从 `.env` 文件读取配置（API Key） |

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

默认源慢就换国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 配置 API Key

```bash
# Windows 命令提示符 / PowerShell
copy .env.example .env
```

然后用文本编辑器打开 `.env`，把 `DEEPSEEK_API_KEY` 改成你自己的 DeepSeek Key。

> 到哪里拿 Key：到 [DeepSeek 开放平台](https://platform.deepseek.com) 注册并创建 API Key。

### 3. 启动

```bash
python main.py
```

看到 `Uvicorn running on http://127.0.0.1:8000` 即启动成功。

### 4. 使用

- **交互文档**：浏览器打开 <http://127.0.0.1:8000/docs>
- **健康检查**：<http://127.0.0.1:8000/health>
- **命令行提问**：

```bash
curl -X POST http://127.0.0.1:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"用一句话解释什么是数据分析\"}"
```

---

## 项目结构

```
ai-tutor/
├── app/
│   ├── __init__.py      # 让 app 成为 Python 包
│   ├── config.py        # 读取配置（API Key、模型名）
│   ├── llm.py           # 封装对 DeepSeek 的调用
│   └── main.py          # FastAPI 应用，定义路由
├── main.py              # 启动脚本（加载 .env 并运行服务）
├── requirements.txt     # 依赖清单
├── .env.example         # 环境变量模板（可提交 GitHub）
├── .env                 # 真实配置（绝不提交！本地生成）
├── .gitignore           # git 忽略规则
└── README.md            # 本文件
```

---

## 你现在学到 / 锻炼了什么（阶段 1）

- ✅ Python 函数、模块、包与 `import` 的组织方式
- ✅ 用环境变量管理密钥（安全习惯）
- ✅ 调用第三方 HTTP API（openai 客户端）
- ✅ 用 FastAPI 定义 REST 接口（GET / POST）
- ✅ 用 Pydantic 定义请求/响应数据结构
- ✅ 读懂并写出带类型注解、docstring 的工程化代码

---

## 安全须知（非常重要）

- **`.env` 里有你的 API Key，绝不能提交到 GitHub**，`.gitignore` 已经帮我们忽略它。
- 提交到 GitHub 的只有 `.env.example`（里面是占位符，没有真实 Key）。
- 每次提交前检查 `git status`，确认 `.env` 没有出现在待提交列表。

---

## 路线图（后续阶段规划）

| 阶段 | 内容 | 学习点 |
|------|------|--------|
| 阶段 2 | AI 能读取/总结上传的 PDF、文档 | 文件上传、PDF 解析 |
| 阶段 3 | 把 AI 做成"智能体"，挂载工具、多轮对话 | 工具调用、异步 async、结构化输出 |
| 阶段 4 | 完善前端、测试、部署到线上 | pytest、前端、部署 |

每个阶段都会新增学习内容，并在本 README 更新进度。

---

## License

本项目仅供学习交流使用。
