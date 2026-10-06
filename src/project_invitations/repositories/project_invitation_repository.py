from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database.base_repository import BaseRepository
from ..models.project_invitation_model import InvitationStatus, ProjectInvitation


class ProjectInvitationRepository(BaseRepository[ProjectInvitation]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProjectInvitation, db)

    async def get_pending_invite(self, project_id: int, invitee_id: int):
        stmt = select(ProjectInvitation).where(
            ProjectInvitation.id_project == project_id,
            ProjectInvitation.id_invitee == invitee_id,
            ProjectInvitation.status == InvitationStatus.PENDING,
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_invite_by_id(self, id: int):
        stmt = select(ProjectInvitation).where(ProjectInvitation.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_invitations_for_invitee(self, invitee_id: int):
        stmt = (
            select(ProjectInvitation)
            .where(
                ProjectInvitation.id_invitee == invitee_id,
                ProjectInvitation.status == InvitationStatus.PENDING,
            )
            .order_by(ProjectInvitation.id.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_token(self, token: str):
        stmt = select(ProjectInvitation).where(ProjectInvitation.token == token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

