from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Admin(Base):
    __tablename__ = "admins"

    user_id: Mapped[int] = mapped_column(nullable=False)
    add_tb: Mapped[bool] = mapped_column(nullable=False)
    edit_tb: Mapped[bool] = mapped_column(nullable=False)
    del_tb: Mapped[bool] = mapped_column(nullable=False)
    add_time: Mapped[bool] = mapped_column(nullable=False)
    edit_time: Mapped[bool] = mapped_column(nullable=False)
    del_time: Mapped[bool] = mapped_column(nullable=False)
    add_source: Mapped[bool] = mapped_column(nullable=False)
    edit_source: Mapped[bool] = mapped_column(nullable=False)
    del_source: Mapped[bool] = mapped_column(nullable=False)
    rerate: Mapped[bool] = mapped_column(nullable=False)
    comments: Mapped[bool] = mapped_column(nullable=False)
    event: Mapped[bool] = mapped_column(nullable=False)
