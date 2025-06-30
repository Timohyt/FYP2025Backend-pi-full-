from models import TrafficLog

def log_traffic(db, lane: int, count: int, duration: int):
    log = TrafficLog(lane=lane, count=count, duration=duration)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
