# file: server/app/schemas.py
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from decimal import Decimal

class OrmConfig(BaseModel):
    class Config:
        from_attributes = True

class Zone(OrmConfig):
    zone_id: str
    name: str
    current_temp: float

class ZoneStatus(Zone):
    recommended_temp: float

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

class VoteStats(BaseModel):
    minus_one: int = Field(alias='-1')
    zero: int = Field(alias='0')
    plus_one: int = Field(alias='1')

class User(OrmConfig):
    user_id: UUID4
    first_seen_at: datetime
    last_seen_at: datetime

class HistoryRecord(OrmConfig):
    timestamp: datetime
    current_temp: float
    recommended_temp: float
