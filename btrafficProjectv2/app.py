from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decision_service import make_decision
from database import get_db, engine
import models
from crud import log_traffic

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now; restrict later in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class VehicleCountInput(BaseModel):
    lane: int
    count: int

@app.post("/api/decision")
def receive_count(data: VehicleCountInput, db: Session = Depends(get_db)):
    duration = make_decision(data.lane, data.count)
    log_traffic(db, lane=data.lane, count=data.count, duration=duration)
    return {"lane": data.lane, "green_duration": duration}
