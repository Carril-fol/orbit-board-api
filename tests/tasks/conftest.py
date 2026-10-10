import pytest

from collaborators.models.collaborators_model import Collaborators
from tasks.models.task_model import Task, TaskPriority
from tasks.repositories.task_repository import TaskRepository
from tasks.repositories.task_user_repository import TaskUserRepository


@pytest.fixture
def task_repo(db_session):
    return TaskRepository(db_session)


@pytest.fixture
def task_user_repo(db_session):
    return TaskUserRepository(db_session)


@pytest.fixture
async def member(second_user, project_created, collaborators_repo):
    await collaborators_repo.create(
        Collaborators(role="MEMBER", id_user=second_user.id, id_project=project_created.id)
    )
    return second_user


@pytest.fixture
def make_task(task_repo, project_created):
    async def _make(**fields) -> Task:
        return await task_repo.create(
            Task(project_id=project_created.id, title="Task", priority=TaskPriority.LOW, **fields)
        )

    return _make
