#models.py
from sqlalchemy import Column, Integer, DateTime, String, TIMESTAMP, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id = Column(Integer, primary_key=True, index=True)
    lane = Column(Integer, index=True, nullable=True)
    count = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message = Column(String, nullable=True)
    event_type = Column(String, nullable=True)  # e.g., 'info', 'error', 'decision'
    control_mode = Column(String, nullable=True)  # e.g., 'auto', 'manual' (add if you want)

class TrafficLogEntry(Base):
    __tablename__ = "traffic_log_entries"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message = Column(String(512), nullable=False)
    lane = Column(Integer, nullable=True)
    event_type = Column(String(64), nullable=True)

class CapturedImage(Base):
    __tablename__ = "captured_images"
    id = Column(Integer, primary_key=True, index=True)
    lane = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    image_data = Column(LargeBinary, nullable=False)

class YoloBoxedImage(Base):
    __tablename__ = "yolo_boxed_images"
    id = Column(Integer, primary_key=True, index=True)
    lane = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    image_data = Column(LargeBinary, nullable=False)

class ManualControlCommand(Base):
    __tablename__ = "manual_control_commands"

    id = Column(Integer, primary_key=True, index=True)
    lane = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    override_timer = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
