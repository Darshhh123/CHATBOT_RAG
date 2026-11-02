import zlib

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session


def next_id(db: Session, model) -> int:
    """Allocate an ID without changing the existing schema (tables have no ID defaults)."""
    key = zlib.crc32(model.__tablename__.encode("utf-8"))
    db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})
    value = db.scalar(select(func.max(model.id)))
    return int(value or 0) + 1


def commit_or_rollback(db: Session) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
