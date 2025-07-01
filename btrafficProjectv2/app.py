from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from passlib.context import CryptContext
from datetime import datetime
import json, base64, os

from database import get_db, engine
import models
from models import AdminUser, TrafficLog, ManualControlCommand
from crud import (
    log_traffic, log_event_to_db,
    save_captured_image, save_yolo_boxed_image,
    get_all_traffic_logs, get_traffic_summary, save_manual_command
)
from decision_service import make_decision
from pitrafficProjectv2.logger import log

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Traffic Management API",
    description="REST API for intelligent traffic light management system",
    version="1.0.0"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure CORS origins from environment variables
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Restrict to specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specify allowed methods
    allow_headers=["*"],
)

# ----------------- SCHEMAS -----------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VehicleCountInput(BaseModel):
    lane: int
    count: int
    captured_image: Optional[str] = None
    boxed_image: Optional[str] = None

class ManualCommand(BaseModel):
    lane: int
    action: str  # eg. "green", "yellow", "red", "emergency"
    override_timer: Optional[int] = None

class ManualCommandResponse(BaseModel):
    lane: int
    action: str
    override_timer: Optional[int]
    timestamp: datetime

    class Config:
        orm_mode = True

class ReportFilter(BaseModel):
    start_date: str
    end_date: str

# ----------------- AUTH -----------------

@app.post("/api/auth/login")
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.email == login_req.email).first()
    if not user or not pwd_context.verify(login_req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "Login successful", "email": user.email}

# ----------------- VEHICLE COUNT & DECISION -----------------

@app.post("/api/decision")
def receive_count(data: VehicleCountInput, db: Session = Depends(get_db)):
    duration = make_decision(data.lane, data.count)
    log_traffic(db, lane=data.lane, count=data.count, duration=duration)
    log_event_to_db(db, "Vehicle count received", lane=data.lane, event_type="decision")
    log(f"Received vehicle count for lane {data.lane}: {data.count}")

    if data.captured_image:
        try:
            captured_bytes = base64.b64decode(data.captured_image)
            save_captured_image(db, lane=data.lane, filename=f"lane{data.lane}_captured_api.jpg", image_data=captured_bytes)
        except Exception as e:
            log_event_to_db(db, f"Error saving captured image: {e}", lane=data.lane, event_type="error")

    if data.boxed_image:
        try:
            boxed_bytes = base64.b64decode(data.boxed_image)
            save_yolo_boxed_image(db, lane=data.lane, filename=f"lane{data.lane}_boxed_api.jpg", image_data=boxed_bytes)
        except Exception as e:
            log_event_to_db(db, f"Error saving YOLO image: {e}", lane=data.lane, event_type="error")

    return {"lane": data.lane, "green_duration": duration, "message": "Decision processed and data stored"}

# ----------------- SYSTEM STATUS POLLING -----------------

@app.get("/api/status")
def get_status():
    try:
        with open("status.json", "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ----------------- REPORTING ENDPOINTS -----------------

@app.get("/api/reports")
def get_reports(db: Session = Depends(get_db)):
    logs = get_all_traffic_logs(db)
    return logs

@app.post("/api/reports/filter")
def get_filtered_reports(filters: ReportFilter, db: Session = Depends(get_db)):
    logs = db.query(TrafficLog).filter(
        TrafficLog.timestamp >= filters.start_date,
        TrafficLog.timestamp <= filters.end_date
    ).all()
    return logs

# ----------------- DASHBOARD ANALYTICS -----------------

@app.get("/api/analytics")
def get_analytics_summary(db: Session = Depends(get_db)):
    summary = get_traffic_summary(db)
    return summary

# ----------------- MANUAL CONTROL ENDPOINTS -----------------

@app.post("/api/manual")
def send_manual_command(cmd: ManualCommand, db: Session = Depends(get_db)):
    log_event_to_db(db, f"Manual control triggered: {cmd.action}", lane=cmd.lane, event_type="manual")
    save_manual_command(db, lane=cmd.lane, action=cmd.action, override_timer=cmd.override_timer)
    return {"message": f"Manual command sent to lane {cmd.lane}", "action": cmd.action}

@app.get("/api/manual", response_model=List[ManualCommandResponse])
def get_manual_commands(db: Session = Depends(get_db)):
    commands = db.query(ManualControlCommand).order_by(ManualControlCommand.timestamp.desc()).all()
    return commands

# ----------------- SYSTEM MONITORING -----------------

@app.get("/api/monitoring")
def get_monitoring_status():
    try:
        with open("monitoring.json", "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
