from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class ProjectTag(Base):
    __tablename__ = "project_tags"
    __table_args__ = (
        UniqueConstraint("id_project", "tag", name="uq_project_tags_project_tag"),
    )
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
