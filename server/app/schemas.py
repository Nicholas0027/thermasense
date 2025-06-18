# file: server/app/schemas.py
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from decimal import Decimal

# --- 配置 ---
# 通用配置，使模型能从ORM对象（数据库记录）中读取数据
# 并将orm_mode更新为新版的from_attributes
class OrmConfig(BaseModel):
    class Config:
        from_attributes = True

# --- Zone Schemas ---
class Zone(OrmConfig):
    zone_id: str
    name: str
    current_temp: float

class ZoneStatus(Zone):
    recommended_temp: float

# --- Vote Schemas ---
class VoteCreate(BaseModel):
    user_id: UUID4
    zone_id: str
    vote_value: int

class Vote(OrmConfig):
    vote_id: int
    user_id: UUID4
    zone_id: str
    vote_value: int
    created_at: datetime

# 【新增】为投票统计接口定义响应模型
class VoteStats(BaseModel):
    minus_one: int = Field(alias='-1')
    zero: int = Field(alias='0')
    plus_one: int = Field(alias='1')

# --- User Schemas ---
class User(OrmConfig):
    user_id: UUID4
    first_seen_at: datetime
    last_seen_at: datetime

# --- History Schemas ---
class HistoryRecord(OrmConfig):
    timestamp: datetime
    current_temp: float
    recommended_temp: float

3. 后端主应用 (server/app/main.py)
这个文件是整个后端应用的入口。它负责初始化FastAPI应用，配置模板，并加载我们定义好的所有API路由。

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
