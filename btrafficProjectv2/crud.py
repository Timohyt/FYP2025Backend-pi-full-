#crud.py
from models import TrafficLog, TrafficLogEntry, CapturedImage, YoloBoxedImage
from datetime import datetime

def log_traffic(db, lane: int = None, count: int = None, duration: int = None, 
                event_type: str = "decision", control_mode: str = "auto", message: str = None):
    if message is None:
        message = f"Decision made for lane {lane}: green for {duration}s with count {count}"
    
    log_entry = TrafficLog(
        lane=lane,
        count=count,
        duration=duration,
        event_type=event_type,
        control_mode=control_mode,
        message=message
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry

def log_event_to_db(db, message: str, lane: int = None, event_type: str = "info", control_mode: str = "auto"):
    entry = TrafficLog(
        message=message,
        lane=lane,
        event_type=event_type,
        control_mode=control_mode
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def save_captured_image(db, lane: int, img_bytes: bytes):
    db_img = CapturedImage(lane=lane, image_data=img_bytes)
    db.add(db_img)
    db.commit()
    db.refresh(db_img)
    return db_img

def save_yolo_boxed_image(db, lane: int, img_bytes: bytes):
    db_img = YoloBoxedImage(lane=lane, image_data=img_bytes)
    db.add(db_img)
    db.commit()
    db.refresh(db_img)
    return db_img

def get_all_traffic_logs(db):
    return db.query(TrafficLog).order_by(TrafficLog.timestamp.desc()).all()

def get_traffic_summary(db):
    total_vehicles = db.query(TrafficLog).filter(TrafficLog.count != None).count()
    total_alerts = db.query(TrafficLog).filter(TrafficLog.event_type == "error").count()
    uptime_minutes = db.query(TrafficLog).count() * 2  # e.g., 1 log = 2 min

    return {
        "total_vehicles": total_vehicles,
        "alert_count": total_alerts,
        "system_uptime_minutes": uptime_minutes,
        "active_cameras": 4  # static or derived from another table in future
    }

def save_manual_command(db, lane: int, action: str, override_timer: int = None):
    from models import ManualControlCommand
    command = ManualControlCommand(
        lane=lane,
        action=action,
        override_timer=override_timer
    )
    db.add(command)
    db.commit()
    db.refresh(command)
    return command
