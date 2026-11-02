from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import Pet, User, Vaccination
from app.schemas.common import VaccinationCreate, VaccinationResponse
from app.services.database import commit_or_rollback, next_id

router = APIRouter(prefix="/vaccinations", tags=["Vaccinations"])
def get_vaccination(db, user, vaccination_id):
    row = db.scalar(select(Vaccination).join(Pet).where(Vaccination.id == vaccination_id))
    if row is None: raise HTTPException(status_code=404, detail="Vaccination not found")
    if user and user.role == "owner" and row.pet.owner_id != user.id: raise HTTPException(status_code=403, detail="Access denied")
    return row
@router.get("/", response_model=list[VaccinationResponse])
def list_vaccinations(pet_id: int | None = None, due: bool = False, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = select(Vaccination).join(Pet)
    if user and user.role == "owner": q = q.where(Pet.owner_id == user.id)
    if pet_id is not None: q = q.where(Vaccination.pet_id == pet_id)
    if due: q = q.where(Vaccination.next_due_date <= date.today())
    return list(db.scalars(q.order_by(Vaccination.next_due_date)).all())
@router.post("/", status_code=201, response_model=VaccinationResponse)
def create_vaccination(payload: VaccinationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pet = db.get(Pet, payload.pet_id)
    if pet is None: raise HTTPException(status_code=404, detail="Pet not found")
    if user and user.role == "owner": raise HTTPException(status_code=403, detail="Only clinic staff can manage vaccinations")
    row = Vaccination(id=next_id(db, Vaccination), **payload.model_dump()); db.add(row); commit_or_rollback(db); return row
@router.put("/{vaccination_id}", response_model=VaccinationResponse)
def update_vaccination(vaccination_id: int, payload: VaccinationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user and user.role == "owner": raise HTTPException(status_code=403, detail="Only clinic staff can manage vaccinations")
    row = get_vaccination(db, user, vaccination_id); [setattr(row,k,v) for k,v in payload.model_dump().items()]; commit_or_rollback(db); return row
@router.delete("/{vaccination_id}")
def delete_vaccination(vaccination_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user and user.role == "owner": raise HTTPException(status_code=403, detail="Only clinic staff can manage vaccinations")
    db.delete(get_vaccination(db,user,vaccination_id)); commit_or_rollback(db); return {"message":"Vaccination deleted successfully"}

