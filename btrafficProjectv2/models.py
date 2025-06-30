from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id = Column(Integer, primary_key=True, index=True)
    lane = Column(Integer, index=True)
    count = Column(Integer)
    duration = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
