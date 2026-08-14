import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from collaborators.models.collaborators_model import Collaborators
from project_invitations.models.project_invitation_model import ProjectInvitation
from projects.models.project import Project
from projects_tags.models.project_tag_model import ProjectTag
from requests.models.requests_model import Request
from users.models.user import User
from tasks.models.task_model import Task
from tasks.models.task_user_model import TaskUser
from comments.models.comment_model import Comment
from audit_logs.models.audit_log_model import AuditLog

from shared.config.settings import settings
from shared.database import Base
from shared.database.database import sanitize_url

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
# Same sanitizing the app does: the Neon URL carries libpq parameters
# (sslmode, channel_binding) that asyncpg does not accept.
config.set_main_option("sqlalchemy.url", sanitize_url(settings.neon_database_url))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    The project uses asyncpg, so the engine and the connection are async and the
    migration itself runs through run_sync.

    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
