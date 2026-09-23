# 🤖 AI Tutor — 私人 AI 学习/生涯助手（Personal AI Copilot）

> 一个以 **FastAPI + DeepSeek 大模型**为基础，逐步进化成"只属于你的 AI 第二大脑"
> 的长期学习与作品集项目。
>
> **当前阶段**：阶段 1 已完成（FastAPI + DeepSeek 最小可运行版，可单次问答）。
> **进化方向**：接入飞书、长期记忆、Canvas 作业 DDL 提醒、比赛/求职推荐、
> 动态简历、3D 可视化界面。

---

## 🎯 项目定位

不是"通用聊天机器人"，而是给你自己（大二学生）用的**私人 AI 生涯助手**：

- 在**飞书**里跟它聊天，记录你每天干了什么
- 它有**长期记忆**，记得你聊过什么、做过什么
- 自动**总结每日**、规划接下来可以干什么
- 接入 **Canvas API**，在作业临近 DDL 时主动提醒你
- 根据你的专业/年级**推荐能打的比赛**、规划学习路线
- 动态**更新简历**，大四时推荐可投的公司与官网
- 用 **3D 可视化界面**（类游戏、可互动）汇总展示一切

---

## 🧩 视觉化路线（每阶段都能跑、能展示）

| 阶段 | 内容 | 状态 |
|------|------|------|
| 阶段 1 | FastAPI + DeepSeek 最小可运行（单次问答）| ✅ 完成 |
| 阶段 2 | 飞书入口 + 日志总结 + 长期记忆 | 🔜 进行中 |
| 阶段 3 | Canvas API + 作业 DDL 提醒 | ⏳ 规划 |
| 阶段 4 | 比赛推荐 + 日程规划（多 Agent） | ⏳ 规划 |
| 阶段 5 | 动态简历 + 求职推荐 | ⏳ 规划 |
| 阶段 6 | 3D 可视化互动界面 | ⏳ 规划 |

> 📄 详细设计见 [`私人AI生涯助手-蓝图.md`](私人AI生涯助手-蓝图.md)
> 📚 学习路线见 [`Python到Agent学习路线图.md`](Python到Agent学习路线图.md)

---

## 🛠️ 技术栈

| 组件 | 作用 |
|------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | 现代 Python Web 框架，自带交互式 API 文档 |
| [Uvicorn](https://www.uvicorn.org/) | ASGI 服务器，用来运行 FastAPI |
| [openai](https://github.com/openai/openai-python) | DeepSeek 官方推荐的 OpenAI 兼容 SDK |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 从 `.env` 文件读取配置（API Key） |

将来会逐步加入：飞书 SDK、SQLite/LanceDB（记忆库）、APScheduler（定时提醒）、Three.js（3D 前端）等。

---

## 🚀 快速开始（阶段 1 现状）

### 1. 安装依赖
```bash
pip install -r requirements.txt
```
国内源慢就加：`-i https://pypi.tuna.tsinghua.edu.cn/simple`

### 2. 配置 API Key
```bash
copy .env.example .env   # Windows
```
打开 `.env`，把 `DEEPSEEK_API_KEY` 改成你的 DeepSeek Key（到 [DeepSeek 开放平台](https://platform.deepseek.com) 申请）。

### 3. 启动
```bash
python main.py
```
看到 `Uvicorn running on http://127.0.0.1:8000` 即成功。

### 4. 使用
- 交互文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>
- 提问：
```bash
curl -X POST http://127.0.0.1:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"用一句话解释什么是数据分析\"}"
```

（也可直接双击 `start.bat` 一键启动；`push.bat` 一键推送 GitHub。）

---

## 📁 项目结构

```
ai-tutor/
├── app/
│   ├── __init__.py      # 让 app 成为 Python 包
│   ├── config.py        # 读取配置（API Key、模型名）
│   ├── llm.py           # 封装对 DeepSeek 的调用
│   ├── memory.py        # 对话记忆模块（summarize_messages 等）
│   └── main.py          # FastAPI 应用，定义路由
├── main.py              # 启动脚本（加载 .env 并运行服务）
├── requirements.txt     # 依赖清单
├── .env                 # 真实配置（绝不提交！）
├── .gitignore           # git 忽略规则
├── README.md            # 本文件
├── 开始使用-完整教程.md   # 新手启动教程
├── Python到Agent学习路线图.md   # 学习路线
└── 私人AI生涯助手-蓝图.md       # 项目发展蓝图
```

---

## 🔒 安全须知（重要）

- **`.env` 里有 API Key，绝不提交到 GitHub**（`.gitignore` 已忽略）。
- 所有未来接入的 token（飞书、Canvas 等）同样只放 `.env`。
- 每次提交前检查 `git status`，确认 `.env` 未出现在列表。

---

## 📈 进度记录

- [x] 阶段 1：FastAPI + DeepSeek 最小可运行（单次问答）
- [ ] 阶段 2：飞书入口 + 日志总结 + 长期记忆
- [ ] 阶段 3：Canvas API + DDL 提醒
- [ ] 阶段 4：比赛推荐 + 规划 Agent
- [ ] 阶段 5：动态简历 + 求职推荐
- [ ] 阶段 6：3D 可视化界面

---

## License

本项目仅供学习交流使用。
