from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import Appointment,Pet,User, Vaccination,Visit
router=APIRouter(prefix="/patients",tags=["Patients"])
def allowed(db,user,pet_id):
    pet=db.scalar(select(Pet).where(Pet.id==pet_id))
    if pet is None:raise HTTPException(status_code=404,detail="Patient not found")
    if user and user.role=="owner" and pet.owner_id!=user.id:raise HTTPException(status_code=403,detail="Access denied")
    return pet
@router.get("/")
def list_patients(search:str|None=None,species:str|None=None,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    q=select(Pet,User).join(User,User.id==Pet.owner_id)
    if user and user.role=="owner":q=q.where(Pet.owner_id==user.id)
    if search:q=q.where(Pet.name.ilike(f"%{search}%"))
    if species:q=q.where(Pet.species.ilike(species))
    return [{"pet":p,"owner":o} for p,o in db.execute(q).all()]
@router.get("/{pet_id}")
def details(pet_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    pet=allowed(db,user,pet_id);owner=db.get(User,pet.owner_id)
    return {"pet":pet,"owner":owner,"appointments":list(db.scalars(select(Appointment).where(Appointment.pet_id==pet_id)).all()),"visits":list(db.scalars(select(Visit).where(Visit.pet_id==pet_id)).all()),"vaccinations":list(db.scalars(select(Vaccination).where(Vaccination.pet_id==pet_id)).all())}
@router.get("/{pet_id}/history")
def history(pet_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    allowed(db,user,pet_id)
    return {"pet_id":pet_id,"visits":list(db.scalars(select(Visit).where(Visit.pet_id==pet_id)).all()),"appointments":list(db.scalars(select(Appointment).where(Appointment.pet_id==pet_id)).all())}

