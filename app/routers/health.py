
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import check_database_connection

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/status")
def status():
    return {"status": "ok"}


@router.get("/db")
def database_status():
    try:
        check_database_connection()
        return {
            "status": "connected",
            "database": "Neon PostgreSQL"
        }
    except (SQLAlchemyError, RuntimeError):
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Check your .env configuration."
        )
