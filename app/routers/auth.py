from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.common import LoginRequest, RegisterRequest, UserResponse
from app.services.auth import create_access_token, hash_password, verify_password
from app.services.database import commit_or_rollback

router = APIRouter(prefix="/auth", tags=["Authentication"])

def public_user(user: User) -> dict:
    return UserResponse.model_validate(user).model_dump()

@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(func.lower(User.email) == email)):
        raise HTTPException(status_code=409, detail="Email address is already registered")
    user = User(full_name=payload.full_name, email=email,
                password_hash=hash_password(payload.password), phone=payload.phone, role="owner", is_active=True)
    db.add(user)
    try:
        commit_or_rollback(db)
        db.refresh(user)
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Email address is already registered") from exc
    return {"message": "Registration successful", "user": public_user(user)}

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
    return {"message": "Login successful", "access_token": create_access_token(user.id), "token_type": "bearer", "user": public_user(user)}

@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

