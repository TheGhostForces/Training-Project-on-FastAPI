from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Model(DeclarativeBase):
    pass


class UsersOrm(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    tasks: Mapped[list["TasksOrm"]] = relationship(back_populates="user", lazy="dynamic")
    sent_messages: Mapped[list["MessageOrm"]] = relationship(back_populates="sender")

class TasksOrm(Model):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]]
    completed: Mapped[bool] = mapped_column(nullable=False, default=False)
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["UsersOrm"] = relationship(back_populates="tasks")

class MessageOrm(Model):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    receiver_username: Mapped[str] = mapped_column(nullable=False)
    sender: Mapped["UsersOrm"] = relationship(back_populates="sent_messages")