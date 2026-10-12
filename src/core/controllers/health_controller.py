from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import DatabaseUnavailable
from shared.database import get_async_db

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Liveness and database probe")
async def health(db: AsyncSession = Depends(get_async_db, scope="function")) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError):
        raise DatabaseUnavailable()
    return {"status": "ok", "database": "ok"}
