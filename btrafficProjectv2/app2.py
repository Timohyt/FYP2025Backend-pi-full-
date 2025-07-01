#app.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from decision_service import make_decision
from passlib.context import CryptContext
from database import get_db, engine
import models
from crud import log_traffic, log_event_to_db, save_captured_image, save_yolo_boxed_image
from pitrafficProjectv2.logger import log
import json
from fastapi.responses import JSONResponse
import base64

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now; restrict later in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VehicleCountInput(BaseModel):
    lane: int
    count: int
    captured_image: Optional[str] = None  # base64-encoded image string
    boxed_image: Optional[str] = None     # base64-encoded image string

@app.post("/api/auth/login")
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.email == login_req.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not pwd_context.verify(login_req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # Authentication success
    # TODO: Implement JWT token generation or session management here
    return {"message": "Login successful", "email": user.email}

@app.post("/api/decision")
def receive_count(data: VehicleCountInput, db: Session = Depends(get_db)):
    duration = make_decision(data.lane, data.count)
    
#log decision result in main log table
    log_traffic(db, lane=data.lane, count=data.count, duration=duration)

#store decision log in DB
    log_event_to_db(db, "Vehicle count received", lane=data.lane, event_type="decision")
    log(f"Received vehicle count for lane {data.lane}: {data.count}")

#Decode and save captured image (if provided)
    if data.captured_image:
        try:
            captured_bytes = base64.b64decode(data.captured_image)
            save_captured_image(
                db,
                lane=data.lane,
                filename=f"lane{data.lane}_captured_api.jpg",
                image_data=captured_bytes
            )
        except Exception as e:
            log_event_to_db(db, f"Failed to save captured image: {e}", lane=data.lane, event_type="error")

#Decode and save YOLO-boxed image (if provided)
    if data.boxed_image:
        try:
            boxed_bytes = base64.b64decode(data.boxed_image)
            save_yolo_boxed_image(
                db,
                lane=data.lane,
                filename=f"lane{data.lane}_boxed_api.jpg",
                image_data=boxed_bytes
            )
        except Exception as e:
            log_event_to_db(db, f"Failed to save YOLO-boxed image: {e}", lane=data.lane, event_type="error")

    return {"lane": data.lane, "green_duration": duration, "message": "Decision processed and data stored"}

#polling
@app.get("/api/status")
def get_status():
    try:
        with open("status.json", "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})  
