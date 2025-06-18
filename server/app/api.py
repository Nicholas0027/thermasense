# file: server/app/api.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import json
from decimal import Decimal

# 导入项目内部模块
from . import models, schemas, crud, strategy
from .database import SessionLocal
# 从main.py中导入templates实例，以避免循环导入
from .main import templates

# 依赖项：这是一个可复用的函数，用于为每个请求提供一个独立的数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 路由组 1: 面向用户的API ---
# 使用 tags 参数可以在API文档中进行分组，非常清晰
user_router = APIRouter(prefix="/api", tags=["User Endpoints"])

@user_router.get("/zones/", response_model=list[schemas.Zone])
def get_zones(db: Session = Depends(get_db)):
    """
    获取所有可用分区的列表，供前端下拉框使用。
    """
    return db.query(models.Zone).all()

# 【BUG修复】修正了装饰器中的拼写错误 (user_-router -> user_router)
@user_router.get("/zones/{zone_id}/status", response_model=schemas.ZoneStatus)
def get_zone_status(zone_id: str, db: Session = Depends(get_db)):
    """
    获取单个分区的详细状态，包括当前温度和推荐温度。
    """
    zone = db.query(models.Zone).filter(models.Zone.zone_id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone

@user_router.post("/vote/", response_model=schemas.Vote)
def submit_vote(vote: schemas.VoteCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    接收一次用户投票，存入数据库，并异步触发核心算法。
    """
    # 检查用户是否存在，如果不存在则创建
    db_user = crud.get_user(db, user_id=vote.user_id)
    if not db_user:
        crud.create_user(db, user_id=vote.user_id)
    else:
        # 如果用户存在，则更新其最近活跃时间
        db_user.last_seen_at = datetime.utcnow()
        db.commit()

    # 检查投票的分区是否存在
    db_zone = db.query(models.Zone).filter(models.Zone.zone_id == vote.zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # 创建投票记录
    new_vote = crud.create_vote(db=db, vote=vote)
    
    # 将耗时的温度计算任务放入后台执行，立即返回响应给用户
    background_tasks.add_task(strategy.calculate_recommended_temperature, db=db, zone_id=vote.zone_id)
    
    return new_vote

@user_router.get("/zones/{zone_id}/stats", response_model=schemas.VoteStats)
def get_vote_stats(zone_id: str, db: Session = Depends(get_db)):
    """
    获取指定分区最近一段时间的投票统计数据，用于前端仪表盘图表。
    """
    # 【BUG修复】使用与核心算法一致的、更可靠的时间计算方式
    time_threshold = datetime.utcnow() - timedelta(minutes=strategy.VOTE_VALID_DURATION_MINUTES)
    results = (
        db.query(models.Vote.vote_value, func.count(models.Vote.vote_id))
        .filter(models.Vote.zone_id == zone_id, models.Vote.created_at >= time_threshold)
        .group_by(models.Vote.vote_value).all()
    )
    counts = {str(value): count for value, count in results}
    # 确保所有投票类型都有返回值
    return {
        "-1": counts.get("-1", 0),
        "0": counts.get("0", 0),
        "1": counts.get("1", 0)
    }

# --- 路由组 2: 面向管理的API ---
admin_router = APIRouter(prefix="/admin", tags=["Admin Panel"])

@admin_router.get("/monitoring-panel", response_class=HTMLResponse)
def get_monitoring_panel(request: Request, db: Session = Depends(get_db)):
    """
    获取并渲染包含所有分区历史数据的监控面板HTML页面。
    """
    all_zones = db.query(models.Zone).all()
    history_data = {}
    time_threshold = datetime.utcnow() - timedelta(hours=1) # 只看最近一小时

    for zone in all_zones:
        history = (
            db.query(models.History)
            .filter(models.History.zone_id == zone.zone_id, models.History.timestamp >= time_threshold)
            .order_by(models.History.timestamp.asc()).all()
        )
        history_data[zone.zone_id] = {
            "name": zone.name,
            "data": [schemas.HistoryRecord.from_orm(h).dict() for h in history]
        }
    
    history_data_json = json.dumps(history_data, default=str) # 使用default=str处理Decimal和DateTime

    return templates.TemplateResponse(
        "monitoring.html", 
        {"request": request, "history_data_json": history_data_json}
    )