from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Admin(Base):
    __tablename__ = "admins"

    admin_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    add_tb: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    edit_tb: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    del_tb: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    add_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    edit_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    del_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    add_source: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    edit_source: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    del_source: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rerate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    comments: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    event: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
