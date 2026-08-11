from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from collaborators.repositories.collaborator_repository import CollaboratorRepository
from projects.repositories.project_repository import ProjectRepository
from tasks.repositories.task_repository import TaskRepository

from .repositories.comment_repository import CommentRepository
from .services.comment_service import CommentService

def get_projects_repository(
    db: AsyncSession = Depends(get_async_db),
):
    return ProjectRepository(db)


def get_collaborators_repository(
    db: AsyncSession = Depends(get_async_db),
):
    return CollaboratorRepository(db)


def get_tasks_repository(
    db: AsyncSession = Depends(get_async_db),
):
    return TaskRepository(db)

def get_comments_repository(
    db: AsyncSession = Depends(get_async_db),
):
    return CommentRepository(db)

def get_comments_service(
    repo: CommentRepository = Depends(get_comments_repository),
    collaborator_repo: CollaboratorRepository = Depends(get_collaborators_repository),
    task_repo: TaskRepository = Depends(get_tasks_repository),
):
    return CommentService(
        repo,
        collaborator_repo,
        task_repo,
    )
