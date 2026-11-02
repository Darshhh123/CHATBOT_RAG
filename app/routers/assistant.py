from fastapi import APIRouter,Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import Appointment,Pet,User,Vaccination
from app.schemas.common import ChatRequest
router=APIRouter(prefix="/assistant",tags=["AI Assistant"])
@router.post("/owner-chat")
def owner_chat(payload:ChatRequest,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    text=payload.message.lower(); pets=list(db.scalars(select(Pet).where(Pet.owner_id==user.id)).all()) if user else list(db.scalars(select(Pet)).all())
    if "vaccin" in text:return {"assistant":"PawCare Assistant","answer":f"You have {sum(1 for p in pets for _ in p.vaccinations)} vaccination records.","mode":"database"}
    if "appointment" in text or "book" in text:return {"assistant":"PawCare Assistant","answer":"Use the appointments endpoint to book or view an appointment for one of your pets.","mode":"database"}
    return {"assistant":"PawCare Assistant","answer":"I can help with your pets, appointments, and vaccination records. For diagnosis or emergencies, contact a veterinarian.","mode":"database"}
@router.post("/clinic-chat")
def clinic_chat(payload:ChatRequest,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    rows=list(db.scalars(select(Appointment).where(Appointment.status=="pending")).all()) if user is None or user.role=="clinic_staff" else []
    return {"assistant":"VetDesk AI","answer":f"There are {len(rows)} pending appointments.","data":rows,"mode":"database"}

