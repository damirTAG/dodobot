from datetime import datetime, time
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    BigInteger, 
    ForeignKey,
    DateTime, 
    Time)
from sqlalchemy.sql import func
from src.database.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    
    country_id = Column(Integer)
    pizzeria_id = Column(Integer)
    
    is_active = Column(Boolean, default=True)
    active_since = Column(DateTime)
    failed_notifications = Column(Integer, default=0)
    
    notification_time = Column(Time, default=time(0, 0))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())