from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import Pet, User
from app.schemas.common import PetCreate, PetResponse
from app.services.database import commit_or_rollback, next_id

router = APIRouter(prefix="/pets", tags=["Pets"])

def owned_pet(db, user, pet_id):
    pet = db.scalar(select(Pet).where(Pet.id == pet_id))
    if pet is None: raise HTTPException(status_code=404, detail="Pet not found")
    if user and user.role == "owner" and pet.owner_id != user.id: raise HTTPException(status_code=403, detail="You do not own this pet")
    return pet

@router.get("/", response_model=list[PetResponse])
def list_pets(owner_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user and user.role == "owner": owner_id = user.id
    return list(db.scalars(select(Pet).where(Pet.owner_id == owner_id) if owner_id is not None else select(Pet)).all())

@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(pet_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return owned_pet(db, user, pet_id)

@router.post("/", status_code=201, response_model=PetResponse)
def create_pet(payload: PetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owner_id = user.id if user and user.role == "owner" else payload.owner_id
    if owner_id is None: raise HTTPException(status_code=422, detail="owner_id is required when authentication is disabled")
    data = payload.model_dump(exclude={"owner_id"})
    pet = Pet(id=next_id(db, Pet), owner_id=owner_id, **data)
    db.add(pet); commit_or_rollback(db); return pet

@router.put("/{pet_id}", response_model=PetResponse)
def update_pet(pet_id: int, payload: PetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pet = owned_pet(db, user, pet_id); [setattr(pet, k, v) for k, v in payload.model_dump().items()]
    commit_or_rollback(db); return pet

@router.delete("/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pet = owned_pet(db, user, pet_id); db.delete(pet); commit_or_rollback(db)
    return {"message": "Pet deleted successfully"}

