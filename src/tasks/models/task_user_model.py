from enum import Enum
from datetime import datetime, timezone

from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class TaskUserStatus(str, Enum):
    ASSIGNED = "ASSIGNED"
    UNASSIGNED = "UNASSIGNED"


class TaskUser(Base):
    __tablename__ = "task_users"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[TaskUserStatus] = mapped_column(
        SQLEnum(TaskUserStatus),
        default=TaskUserStatus.ASSIGNED.value,
        nullable=True,
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )