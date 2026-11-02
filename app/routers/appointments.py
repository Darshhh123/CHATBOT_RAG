from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import clinic_for_user, get_current_user
from app.models import Appointment, Clinic, Pet, Service, User, Visit
from app.schemas.common import AppointmentCreate, AppointmentResponse, AppointmentStatus, VisitCreate
from app.services.database import commit_or_rollback, next_id
router = APIRouter(prefix="/appointments", tags=["Appointments"])
VALID_STATUSES={"pending","confirmed","rejected","completed","cancelled"}
def get_appointment(db,user,appointment_id):
    row=db.scalar(select(Appointment).join(Pet).where(Appointment.id==appointment_id))
    if row is None: raise HTTPException(status_code=404,detail="Appointment not found")
    if user and user.role=="owner" and row.pet.owner_id!=user.id: raise HTTPException(status_code=403,detail="Access denied")
    if user and user.role=="clinic_staff": clinic_for_user(db,user,row.clinic_id)
    return row
@router.get("/",response_model=list[AppointmentResponse])
def list_appointments(status:str|None=None,pet_id:int|None=None,appointment_date:date|None=None,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    q=select(Appointment).join(Pet)
    if user and user.role=="owner": q=q.where(Pet.owner_id==user.id)
    elif user:
        clinics=list(user.memberships)
        q=q.where(Appointment.clinic_id.in_([m.clinic_id for m in clinics])) if clinics else q.where(False)
    if status: q=q.where(Appointment.status==status)
    if pet_id is not None:q=q.where(Appointment.pet_id==pet_id)
    if appointment_date:q=q.where(Appointment.appointment_date==appointment_date)
    return list(db.scalars(q.order_by(Appointment.appointment_date,Appointment.start_time)).all())
@router.get("/{appointment_id}",response_model=AppointmentResponse)
def get_one(appointment_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)): return get_appointment(db,user,appointment_id)
@router.post("/",status_code=201,response_model=AppointmentResponse)
def create(payload:AppointmentCreate,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    pet=db.get(Pet,payload.pet_id)
    if pet is None:raise HTTPException(status_code=404,detail="Pet not found")
    if user and user.role=="owner" and pet.owner_id!=user.id:raise HTTPException(status_code=403,detail="You do not own this pet")
    if user and user.role=="clinic_staff":clinic_for_user(db,user,payload.clinic_id)
    if db.get(Clinic,payload.clinic_id) is None:raise HTTPException(status_code=404,detail="Clinic not found")
    if payload.service_id is not None and db.scalar(select(Service).where(Service.id==payload.service_id,Service.clinic_id==payload.clinic_id)) is None:raise HTTPException(status_code=404,detail="Service not found for clinic")
    row=Appointment(id=next_id(db,Appointment),status="pending",**payload.model_dump());db.add(row);commit_or_rollback(db);return row
@router.patch("/{appointment_id}/status",response_model=AppointmentResponse)
def update_status(appointment_id:int,payload:AppointmentStatus,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if payload.status not in VALID_STATUSES:raise HTTPException(status_code=422,detail=f"Status must be one of {sorted(VALID_STATUSES)}")
    if user and user.role=="owner":raise HTTPException(status_code=403,detail="Only clinic staff can update appointment status")
    row=get_appointment(db,user,appointment_id);row.status=payload.status;commit_or_rollback(db);return row
@router.post("/{appointment_id}/complete")
def complete(appointment_id:int,payload:VisitCreate,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if user and user.role=="owner":raise HTTPException(status_code=403,detail="Only clinic staff can complete appointments")
    row=get_appointment(db,user,appointment_id)
    if row.status=="completed":raise HTTPException(status_code=409,detail="Appointment is already completed")
    if payload.pet_id!=row.pet_id:raise HTTPException(status_code=422,detail="Visit pet_id must match appointment")
    visit=Visit(id=next_id(db,Visit),appointment_id=row.id,**payload.model_dump());row.status="completed";db.add(visit);commit_or_rollback(db)
    return {"message":"Appointment completed and visit created","appointment":row,"visit":visit}

