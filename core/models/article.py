from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Article(Base):
    __tablename__ = "articles"

    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text)
