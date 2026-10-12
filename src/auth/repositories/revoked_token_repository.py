from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.revoked_token_model import RevokedToken


class RevokedTokenRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def revoke(self, jti: str, expires_at: datetime) -> bool:
        # Check and revoke in one statement, so two concurrent refreshes with the
        # same token cannot both pass. False means it was already revoked.
        stmt = (
            insert(RevokedToken)
            .values(jti=jti, expires_at=expires_at)
            .on_conflict_do_nothing(index_elements=[RevokedToken.jti])
            .returning(RevokedToken.jti)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def is_revoked(self, jti: str) -> bool:
        return await self.db.get(RevokedToken, jti) is not None

    async def purge_expired(self) -> None:
        await self.db.execute(
            delete(RevokedToken).where(RevokedToken.expires_at < datetime.now(timezone.utc))
        )
