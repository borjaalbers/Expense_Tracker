from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    expenses: Mapped[list[Expense]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="Uncategorized")
    date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    note: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    user: Mapped[User] = relationship(back_populates="expenses")

    __table_args__ = (
        Index("ix_expenses_user_date", "user_id", "date"),
        UniqueConstraint("id", name="uq_expenses_id"),
    )


