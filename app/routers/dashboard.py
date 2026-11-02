from datetime import date
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import Appointment,ClinicMember,Pet,User,Vaccination
router=APIRouter(prefix="/dashboard",tags=["Dashboard"])
@router.get("/owner")
def owner(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if user and user.role!="owner":raise HTTPException(status_code=403,detail="Owner access required")
    pets=list(db.scalars(select(Pet).where(Pet.owner_id==user.id)).all()) if user else list(db.scalars(select(Pet)).all());ids=[p.id for p in pets]
    return {"pets":pets,"upcoming_appointments":list(db.scalars(select(Appointment).where(Appointment.pet_id.in_(ids),Appointment.appointment_date>=date.today(),Appointment.status.in_(["pending","confirmed"])).order_by(Appointment.appointment_date,Appointment.start_time)).all()) if ids else [],"vaccinations":list(db.scalars(select(Vaccination).where(Vaccination.pet_id.in_(ids)).order_by(Vaccination.next_due_date)).all()) if ids else []}
@router.get("/clinic")
def clinic(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if user and user.role!="clinic_staff":raise HTTPException(status_code=403,detail="Clinic staff access required")
    ids=list(db.scalars(select(ClinicMember.clinic_id).where(ClinicMember.user_id==user.id)).all()) if user else list(db.scalars(select(ClinicMember.clinic_id)).all())
    today=date.today();q=select(Appointment).where(Appointment.clinic_id.in_(ids)) if ids else select(Appointment).where(False)
    rows=list(db.scalars(q).all());upcoming=[a for a in rows if a.appointment_date>=today and a.status in {"pending","confirmed"}]
    due=db.scalar(select(func.count()).select_from(Vaccination).join(Pet).join(Appointment,Appointment.pet_id==Pet.id,isouter=True).where(Vaccination.next_due_date<today)) or 0
    return {"total_patients":db.scalar(select(func.count()).select_from(Pet)) or 0,"total_appointments":len(rows),"today_appointments":sum(a.appointment_date==today for a in rows),"pending_appointments":sum(a.status=="pending" for a in rows),"overdue_vaccinations":due,"upcoming_appointments":sorted(upcoming,key=lambda a:(a.appointment_date,a.start_time))[:5]}

