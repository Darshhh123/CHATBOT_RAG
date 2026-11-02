from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import Service, User

router = APIRouter(prefix="/services", tags=["Clinic Services"])
@router.get("/")
def list_services(active_only: bool = True, clinic_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(Service)
    if active_only: query = query.where(Service.is_active.is_(True))
    if clinic_id is not None: query = query.where(Service.clinic_id == clinic_id)
    return list(db.scalars(query.order_by(Service.name)).all())

