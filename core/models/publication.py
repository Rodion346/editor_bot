from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey
from thematic_block import ThematicBlock

from .base import Base


class Publication(Base):
    __tablename__ = "publications"

    time: Mapped[DateTime] = mapped_column()
    thematic_block_id: Mapped[int] = mapped_column(
        ForeignKey("thematic_blocks.id"), nullable=False
    )

    thematic_block: Mapped["ThematicBlock"] = relationship("ThematicBlock")
