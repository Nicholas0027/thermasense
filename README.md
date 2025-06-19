# 🌡️ ThermaSense

> 智能热舒适度感知与调节系统  
> A Smart Thermal Comfort Feedback & Recommendation Platform built with **FastAPI** + **React**

![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Stack](https://img.shields.io/badge/TechStack-FastAPI%20%7C%20React%20%7C%20PostgreSQL-blue)

---

## 📸 项目预览

> 示例截图（请在 `assets/` 目录中放入相应图片）

| 投票界面 | 仪表盘 |
|:--------:|:------:|
| ![Voting](./assets/demo-vote.png) | ![Dashboard](./assets/demo-dashboard.png) |

---

## 📖 项目简介

**ThermaSense** 是一个基于用户即时反馈的热舒适度调节系统，通过用户投票感知冷暖，自动计算推荐温度，并提供可视化的仪表盘管理界面。

- 🧠 用户投票（偏冷 / 舒适 / 偏热）
- 🧮 实时推荐温度算法
- 📊 分区状态仪表盘与历史趋势
- 🧑‍💼 管理员监控面板

---

## 🏗️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React, Chart.js |
| 后端 | FastAPI, SQLAlchemy |
| 数据库 | PostgreSQL |
| 部署 | Docker, Docker Compose |

---

## 🚀 快速开始

### ✅ 克隆项目

git clone https://github.com/Nicholas0027/thermasense.git
cd thermasense
✅ 配置环境变量
复制 .env.example 并重命名为 .env，设置数据库环境变量：

env
复制
编辑
POSTGRES_DB=thermasense
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
✅ 构建并运行服务
bash
复制
编辑
docker-compose up --build
✅ 访问服务
服务	地址
用户前端页面	http://localhost:3000
后端 API 文档	http://localhost:8000/docs
管理员面板	http://localhost:8000/admin/monitoring-panel

🧠 核心功能
👤 用户功能
自动生成匿名用户 ID（UUID）

支持投票：偏冷、舒适、偏热

实时查看当前温度与推荐温度

投票数据可视化（饼图）

🛠 管理功能
查看所有分区推荐温度

实时投票统计（近 15 分钟）

管理员可手动触发推荐温度计算

历史数据记录（默认 1 小时）

🧮 算法说明
推荐温度计算基于投票加权平均：

python
复制
编辑
# 示例：投票数统计
votes = {-1: 4, 0: 10, 1: 6}
# 当前温度 = 24.0°C，推荐变化权重 = ±0.5°C
recommendation = 24.0 + 0.5 * ((-1 * 4 + 1 * 6) / (4 + 10 + 6))
该算法确保：

多票平衡偏差：支持中立（0）影响

非线性聚合：未来可接入权重模型（如用户等级、时间加权等）

🧪 API 示例
获取分区列表
http
复制
编辑
GET /api/zones/
提交投票
http
复制
编辑
POST /api/vote/
Content-Type: application/json

{
  "user_id": "UUID",
  "zone_id": "Room101",
  "vote_value": -1
}
获取分区状态
http
复制
编辑
GET /api/zones/{zone_id}/status
获取投票统计
http
复制
编辑
GET /api/zones/{zone_id}/stats
📁 项目结构
bash
复制
编辑
thermasense/
├── client/               # 前端 React 应用
│   └── src/App.js
├── server/
│   └── app/
│       ├── main.py       # FastAPI 应用入口
│       ├── api.py        # 所有 API 路由
│       ├── models.py     # 数据模型 (SQLAlchemy)
│       ├── schemas.py    # 数据序列化 (Pydantic)
│       ├── strategy.py   # 推荐温度算法
│       └── templates/    # 管理员监控 HTML 模板
├── docker-compose.yml    # Docker 编排配置
├── .env                  # 环境变量文件
└── README.md
🧑‍💻 本地开发
bash
复制
编辑
# 启动后端 (FastAPI)
cd server
uvicorn app.main:app --reload

# 启动前端 (React)
cd client
npm install
npm start
✅ 生产部署建议
使用 Nginx 反向代理端口并开启 HTTPS

前后端拆分独立部署（CDN + Gunicorn）

监控推荐算法运行日志 & 错误追踪

使用 pg_dump 定期备份数据库

🤝 贡献指南
欢迎提出 Issue、提交 Pull Request、优化推荐算法或改进 UI！

bash
复制
编辑
git checkout -b feature/your-feature
git commit -m "feat: 描述"
git push origin feature/your-feature
