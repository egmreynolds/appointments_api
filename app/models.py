from sqlalchemy import Column, Integer, String, DateTime, Date, Time
from sqlalchemy.sql import func

from .database import Base

class Appointment(Base):
    __tablename__ = "appointments"
    
    aid = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(String, unique = True, index = True)
    description = Column(String)
    date = Column(Date, index = True)
    start_time = Column(Time)
    end_time = Column(Time)
    created_at = Column(DateTime(timezone = True), server_default = func.now())


