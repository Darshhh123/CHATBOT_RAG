from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models import ClinicMember, User
from app.services.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User | None:
    if not token and not settings.AUTH_REQUIRED:
        return None
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    try:
        user_id = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc), headers={"WWW-Authenticate": "Bearer"}) from exc
    user = db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))
    if user is None:
        raise HTTPException(status_code=401, detail="User is inactive or does not exist")
    return user

def require_roles(*roles):
    def dependency(user: User | None = Depends(get_current_user)) -> User | None:
        if user is None and not settings.AUTH_REQUIRED:
            return None
        if user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency

def clinic_for_user(db: Session, user: User, clinic_id: int) -> ClinicMember:
    membership = db.scalar(select(ClinicMember).where(ClinicMember.user_id == user.id, ClinicMember.clinic_id == clinic_id))
    if membership is None:
        raise HTTPException(status_code=403, detail="You are not a member of this clinic")
    return membership
