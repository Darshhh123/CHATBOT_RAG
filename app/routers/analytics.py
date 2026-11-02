from fastapi import APIRouter,Depends
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import Appointment,Pet,User,Visit,Vaccination
router=APIRouter(prefix="/analytics",tags=["Analytics"])
@router.get("/overview")
def overview(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return {"appointments_by_status":dict(db.execute(select(Appointment.status,func.count()).group_by(Appointment.status)).all()),"pets_by_species":dict(db.execute(select(Pet.species,func.count()).group_by(Pet.species)).all()),"total_pets":db.scalar(select(func.count()).select_from(Pet)) or 0,"total_visits":db.scalar(select(func.count()).select_from(Visit)) or 0,"total_vaccinations":db.scalar(select(func.count()).select_from(Vaccination)) or 0}

