# file: server/app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from uuid import UUID

# --- User CRUD ---
def get_user(db: Session, user_id: UUID):
    # 根据user_id查询用户
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def create_user(db: Session, user_id: UUID):
    # 创建一个新用户
    db_user = models.User(user_id=user_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Vote CRUD ---
def create_vote(db: Session, vote: schemas.VoteCreate):
    # 创建一条新的投票记录
    db_vote = models.Vote(
        user_id=vote.user_id,
        zone_id=vote.zone_id,
        vote_value=vote.vote_value
    )
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote