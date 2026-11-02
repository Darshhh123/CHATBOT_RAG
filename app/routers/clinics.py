from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import Clinic, ClinicMember, User

router = APIRouter(prefix="/clinics", tags=["Clinics"])

@router.get("/")
def list_clinics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list(db.scalars(select(Clinic).order_by(Clinic.name)).all())

@router.get("/{clinic_id}")
def get_clinic(clinic_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    clinic = db.get(Clinic, clinic_id)
    if clinic is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic

@router.get("/{clinic_id}/members")
def list_members(clinic_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user and user.role == "owner":
        raise HTTPException(status_code=403, detail="Clinic member details are restricted")
    if user and db.scalar(select(ClinicMember).where(ClinicMember.clinic_id == clinic_id, ClinicMember.user_id == user.id)) is None:
        raise HTTPException(status_code=403, detail="You are not a member of this clinic")
    return list(db.scalars(select(ClinicMember).where(ClinicMember.clinic_id == clinic_id)).all())
