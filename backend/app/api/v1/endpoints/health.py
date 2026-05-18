from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import engine

router = APIRouter()

@router.get("")
async def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status}
