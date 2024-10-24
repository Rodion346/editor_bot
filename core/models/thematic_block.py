from sqlalchemy import ARRAY, String, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ThematicBlock(Base):
    __tablename__ = "thematic_blocks"

    name: Mapped[str] = mapped_column(nullable=False)
    source: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    time_back: Mapped[int] = mapped_column(Integer)
