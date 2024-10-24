from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey
from .thematic_block import ThematicBlock
from datetime import datetime, date
from .base import Base


class Publication(Base):
    __tablename__ = "publications"

    time: Mapped[str] = mapped_column(nullable=False)
    thematic_block_id: Mapped[str] = mapped_column(
        ForeignKey("thematic_blocks.id"), nullable=False
    )
    today: Mapped[int] = mapped_column(nullable=False)

    thematic_block: Mapped["ThematicBlock"] = relationship("ThematicBlock")
