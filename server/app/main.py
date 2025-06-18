# file: server/app/main.py
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from .database import engine
from . import models

# 这句必须放在api导入之前，因为它依赖main.py中的templates
templates = Jinja2Templates(directory="app/templates")

from . import api # 现在可以安全地导入api了

# 在应用启动时，根据models.py中的定义，自动在数据库中创建所有表
models.Base.metadata.create_all(bind=engine)

# 初始化FastAPI应用实例
app = FastAPI(
    title="ThermaSense API",
    description="智能热舒适度调节系统的后端API服务",
    version="1.0.0"
)

# 将定义在api.py中的两个路由组（用户端和管理端）包含到主应用中
app.include_router(api.user_router)
app.include_router(api.admin_router)

# 定义一个根路径，用于快速检查服务是否正常运行
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to ThermaSense API!",
        "docs_url": "/docs",
        "monitoring_panel_url": "/admin/monitoring-panel"
    }
