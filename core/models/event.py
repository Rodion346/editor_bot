from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Event(Base):
    __tablename__ = "events"

    name: Mapped[str] = mapped_column(nullable=False)
    source: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
