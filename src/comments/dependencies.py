from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from collaborators.dependencies import get_collaborators_service
from collaborators.interfaces import ICollaboratorService
from tasks.dependencies import get_task_service
from tasks.interfaces import ITaskService

from audit_logs.dependencies import get_audit_log_service
from audit_logs.interfaces import IAuditLogService

from .interfaces import ICommentService
from .repositories.comment_repository import CommentRepository
from .services.comment_service import CommentService


def get_comments_repository(db: AsyncSession = Depends(get_async_db)) -> CommentRepository:
    return CommentRepository(db)


def get_comments_service(
    repo: CommentRepository = Depends(get_comments_repository),
    collaborator_service: ICollaboratorService = Depends(get_collaborators_service),
    audit_log_service: IAuditLogService = Depends(get_audit_log_service),
    task_service: ITaskService = Depends(get_task_service)
) -> ICommentService:
    return CommentService(repo, collaborator_service, audit_log_service, task_service)
