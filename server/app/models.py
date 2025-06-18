# file: server/app/models.py
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Numeric, SmallInteger, DateTime, ForeignKey,
    Integer, Float, text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_seen_at = Column(DateTime, server_default=text('now()'))
    last_seen_at = Column(DateTime, server_default=text('now()'), onupdate=text('now()'))

    votes = relationship("Vote", back_populates="user")


class Zone(Base):
    __tablename__ = "zones"

    zone_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    current_temp = Column(Numeric(4, 1), nullable=False)
    recommended_temp = Column(Numeric(4, 1), nullable=False)

    votes = relationship("Vote", back_populates="zone")
    history = relationship("History", back_populates="zone")


class Vote(Base):
    __tablename__ = "votes"

    vote_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    zone_id = Column(String, ForeignKey("zones.zone_id"))
    vote_value = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime, server_default=text('now()'), nullable=False)

    user = relationship("User", back_populates="votes")
    zone = relationship("Zone", back_populates="votes")


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String, ForeignKey("zones.zone_id"), nullable=False)
    current_temp = Column(Float, nullable=False)
    recommended_temp = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    zone = relationship("Zone", back_populates="history")