import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from collaborators.models.collaborators_model import Collaborators
from comments.repositories.comment_repository import CommentRepository
from tasks.repositories.task_repository import TaskRepository

TASK_DATA = {
    "title": "Task tests",
    "description": "Task description",
    "status": "TO DO",
    "priority": "MEDIUM",
}


@pytest.fixture
def comment_data():
    return {"content": "Test comment"}


@pytest.fixture
def comments_repo(db_session: AsyncSession):
    return CommentRepository(db_session)


@pytest.fixture
async def task_created(authenticated_client, project_created, db_session):
    await authenticated_client.post(
        f"/projects/api/v1/{project_created.id}/tasks",
        json=TASK_DATA,
    )
    tasks = await TaskRepository(db_session).get_tasks_by_project(project_created.id)
    return tasks[0]


@pytest.fixture
async def second_collaborator(second_user, project_created, collaborators_repo):
    collaborator = Collaborators(
        role="MEMBER",
        id_user=second_user.id,
        id_project=project_created.id,
    )
    return await collaborators_repo.create(collaborator)


@pytest.fixture
async def comment_created(authenticated_client, task_created, comment_data, comments_repo):
    await authenticated_client.post(
        f"/tasks/api/v1/{task_created.id}/comments",
        json=comment_data,
    )
    comments = await comments_repo.get_comments_by_task_id(task_created.id)
    return comments[0]
