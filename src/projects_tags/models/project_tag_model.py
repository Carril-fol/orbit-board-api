from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class ProjectTag(Base):
    __tablename__ = "project_tags"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    id_project: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    tag: Mapped[str] = mapped_column(String(100))
