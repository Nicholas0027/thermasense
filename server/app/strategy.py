# file: server/app/strategy.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from uuid import UUID
from decimal import Decimal
from . import models, crud, hvac_controller

# --- 可配置的策略参数 ---
# 您可以在这里修改这些值，来调整算法的行为

# 数据有效期：只考虑最近15分钟内的投票
VOTE_VALID_DURATION_MINUTES = 15
# 计算阈值：至少有3票才进行一次有效的温度计算
MIN_VALID_VOTES_TO_CALCULATE = 3

# 固定用户定义：首次投票超过7天，且总投票数超过5次
FREQUENT_USER_DAYS_THRESHOLD = 7
FREQUENT_USER_VOTES_THRESHOLD = 5

# 用户权重
WEIGHT_FREQUENT_USER = 1.5 # 固定用户的投票权重
WEIGHT_NORMAL_USER = 1.0   # 临时访客的投票权重

# 温度调节因子
TEMPERATURE_ADJUSTMENT_FACTOR = 0.5 # 基础调节系数 α
MAX_TEMP_CHANGE_PER_CYCLE = 0.8 # 为防止温度剧烈波动，限制单次最大调整幅度

# -------------------------

def _load_user_activity(db: Session, user_ids: list[UUID]) -> dict:
    """
    【性能优化】通过一次数据库查询，批量加载所有相关用户的活跃度信息。
    这避免了在循环中频繁查询数据库，是提升性能的关键。
    """
    # 1. 一次性获取所有相关的用户信息
    users = {u.user_id: u for u in db.query(models.User).filter(models.User.user_id.in_(user_ids)).all()}
    
    # 2. 一次性统计所有相关用户的总投票数
    vote_counts = dict(
        db.query(models.Vote.user_id, func.count(models.Vote.vote_id))
        .filter(models.Vote.user_id.in_(user_ids))
        .group_by(models.Vote.user_id)
        .all()
    )

    # 3. 在内存中进行逻辑判断，组装最终结果
    threshold_time = datetime.utcnow() - timedelta(days=FREQUENT_USER_DAYS_THRESHOLD)
    activity_map = {}
    for user_id, user in users.items():
        count = vote_counts.get(user_id, 0)
        is_frequent = (user.first_seen_at < threshold_time) and (count >= FREQUENT_USER_VOTES_THRESHOLD)
        activity_map[user_id] = {'is_frequent': is_frequent}
        
    return activity_map

def _simulate_physical_temperature_change(zone: models.Zone):
    """
    【模拟物理世界】
    这个函数模拟“当前物理温度”会随着时间的推移，缓慢地向“系统推荐温度”靠拢。
    这会让我们的监控面板看起来更真实。
    """
    if zone.current_temp == zone.recommended_temp:
        return
        
    # 计算温差，并让当前温度向推荐温度靠近一小步（例如温差的10%）
    diff = zone.recommended_temp - zone.current_temp
    change = diff * Decimal('0.1')
    
    # 为了防止变化过快，可以设置一个上限
    if abs(change) > 0.2:
        change = Decimal('0.2') if change > 0 else Decimal('-0.2')
    
    zone.current_temp += change


def calculate_recommended_temperature(db: Session, zone_id: str):
    """
    【核心算法】
    这是系统的大脑。它负责分析一个分区的数据，并计算出新的推荐温度。
    """
    # 步骤 1: 获取分区对象
    zone = db.query(models.Zone).filter(models.Zone.zone_id == zone_id).first()
    if not zone:
        print(f"❌ 错误: 找不到分区 {zone_id}")
        return

    # 步骤 2: (可选, 用于模拟) 更新当前物理温度
    _simulate_physical_temperature_change(zone)

    # 步骤 3: 获取近期所有有效投票
    time_threshold = datetime.utcnow() - timedelta(minutes=VOTE_VALID_DURATION_MINUTES)
    recent_votes = db.query(models.Vote).filter(
        models.Vote.zone_id == zone_id,
        models.Vote.created_at >= time_threshold
    ).all()

    # 步骤 4: 检查是否有足够的票数来进行有效计算
    if len(recent_votes) < MIN_VALID_VOTES_TO_CALCULATE:
        print(f"ℹ️ Zone {zone_id}: 投票数不足({len(recent_votes)}/{MIN_VALID_VOTES_TO_CALCULATE})，跳过本次计算。")
        return

    # 步骤 5: 批量获取所有投票者的用户类型
    user_ids = list({v.user_id for v in recent_votes})
    user_activity = _load_user_activity(db, user_ids)
    
    # 步骤 6: 计算加权平均分 (S_zone)
    total_weight, weighted_vote_sum = 0, 0
    for vote in recent_votes:
        is_frequent = user_activity.get(vote.user_id, {}).get('is_frequent', False)
        weight = WEIGHT_FREQUENT_USER if is_frequent else WEIGHT_NORMAL_USER
        weighted_vote_sum += vote.vote_value * weight
        total_weight += weight

    if total_weight == 0:
        return

    avg_score = weighted_vote_sum / total_weight
    
    # 步骤 7: 根据平均分，动态调整温度系数alpha，使系统在偏冷时响应更快
    alpha = 0.7 if avg_score < -0.5 else TEMPERATURE_ADJUSTMENT_FACTOR

    # 步骤 8: 计算温度变化量，并限制单次最大调整幅度
    change = alpha * avg_score
    if abs(change) > MAX_TEMP_CHANGE_PER_CYCLE:
        change = MAX_TEMP_CHANGE_PER_CYCLE if change > 0 else -MAX_TEMP_CHANGE_PER_CYCLE
    
    # 步骤 9: 计算新的推荐温度
    # 核心逻辑：新的推荐温度是在“上一次的推荐温度”基础上进行微调，而不是基于物理温度。
    # 这能保证系统的调节是平滑、渐进的，避免因物理温度的短期波动而产生剧烈震荡。
    new_temp = float(zone.recommended_temp) + change
    
    # 步骤 10: 只有在推荐温度确实发生变化时，才执行更新
    if abs(zone.recommended_temp - Decimal(new_temp)) > 0.05:
        zone.recommended_temp = round(new_temp, 1)

        # 记录本次决策到历史表
        history_record = models.History(
            zone_id=zone_id,
            current_temp=zone.current_temp,
            recommended_temp=zone.recommended_temp
        )
        db.add(history_record)
        
        # 一次性提交所有更改到数据库
        db.commit()

        print(f"✅ Zone '{zone_id}' 推荐温度更新为: {zone.recommended_temp}°C (基于 {len(recent_votes)} 票)")
        
        # 步骤 11: 调用硬件控制器，发出物理调节指令
        hvac_controller.set_zone_temperature(zone_id, zone.recommended_temp)

def calculate_all_zones(db: Session):
    """
    【管理功能】一个方便的工具函数，用于一次性触发所有分区的温度计算。
    未来可以设置一个定时任务来周期性地调用它。
    """
    zones = db.query(models.Zone).all()
    print(f"\n--- 开始周期性地为所有 {len(zones)} 个分区计算推荐温度 ---")
    for zone in zones:
        calculate_recommended_temperature(db, zone.zone_id)
    print("--- 周期性计算完成 ---\n")