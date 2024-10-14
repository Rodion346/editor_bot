from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Event(Base):
    __tablename__ = "events"

    name: Mapped[str] = mapped_column(nullable=False)
    source: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    time_in: Mapped[str] = mapped_column(nullable=False)
    time_out: Mapped[str] = mapped_column(nullable=False)
