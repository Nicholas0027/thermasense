# 🌡️ ThermaSense

> 智能热舒适度感知与调节系统  
> A Smart Thermal Comfort Feedback & Recommendation Platform built with FastAPI + React

![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Stack](https://img.shields.io/badge/TechStack-FastAPI%20%7C%20React%20%7C%20PostgreSQL-blue)

---

## 📸 项目预览

| 投票界面 | 仪表盘 |
|:--------:|:------:|
| ![投票示意](./assets/vote-view.png) | ![仪表盘](./assets/dashboard-view.png) |

---

## 🧩 项目简介

**ThermaSense** 是一个结合用户反馈与实时计算的热舒适度反馈系统。

- 用户通过投票提交冷热感受
- 后端算法动态计算推荐温度
- 管理员可通过监控界面查看各区域历史温度变化

---

## 🧱 技术栈

- **前端**：React + Chart.js + TailwindCSS  
- **后端**：FastAPI + SQLAlchemy + Pydantic  
- **数据库**：PostgreSQL  
- **部署**：Docker + Docker Compose

---

## 🚀 快速启动

1. 克隆项目

    git clone https://github.com/Nicholas0027/thermasense.git  
    cd thermasense

2. 配置环境变量

创建 `.env` 文件，内容如下：

    POSTGRES_USER=youruser
    POSTGRES_PASSWORD=yourpassword
    POSTGRES_DB=thermasense
    DB_HOST=db
    DB_PORT=5432

3. 启动服务

    docker-compose up --build -d

4. 打开浏览器：

- 前端页面（投票 + 仪表盘）：
  
      http://localhost:3000

- 后端接口文档（FastAPI 自动生成）：

      http://localhost:8000/docs

- 管理员监控面板：

      http://localhost:8000/admin/monitoring-panel

---

## 📁 项目结构

    thermaSense/
    ├── client/             # 前端 React 应用
    │   └── src/App.js
    ├── server/             # 后端 FastAPI 应用
    │   ├── app/
    │   │   ├── api.py
    │   │   ├── crud.py
    │   │   ├── database.py
    │   │   ├── models.py
    │   │   ├── schemas.py
    │   │   ├── strategy.py
    │   │   └── main.py
    │   └── Dockerfile
    ├── docker-compose.yml
    ├── .env
    └── README.md

---

## 🧠 核心功能

- 🔘 匿名用户本地生成 UUID 存储身份  
- 📊 投票数据实时更新前端仪表盘  
- ⚙️ 后端通过策略算法计算推荐温度  
- 🕒 数据自动写入 `history` 表形成时间序列  
- 🧑‍💼 管理界面展示每小时历史数据变化

---

## 🧪 开发者说明

### 重建数据库表结构（仅首次）

运行一次 `init_db.py` 或在 `main.py` 中调用：

```python
models.Base.metadata.create_all(bind=engine)
```

### 重启后台服务

    docker-compose restart

---

## 🛡️ 授权协议

本项目采用 **MIT License** 开源许可。你可以自由使用、修改和发布代码，但请保留原始作者署名。

---

## 💡 贡献建议

欢迎提交 issue 或 pull request！你可以贡献的方向包括但不限于：

- UI/UX 优化
- 温控策略算法增强
- 管理面板图表增强
- 多语言支持（i18n）

---

## 🧑‍💻 作者

Nicholas0027 (https://github.com/Nicholas0027)

感谢所有帮助测试、反馈和改进的朋友 🙏

---
