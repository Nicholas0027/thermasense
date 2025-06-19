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
