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




class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # Stored as YYYY-MM for simplicity and efficient lookups
    month: Mapped[str] = mapped_column(String(7), nullable=False)
    limit_amount: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped[User] = relationship(backref="budgets")

    __table_args__ = (
        UniqueConstraint("user_id", "month", name="uq_budgets_user_month"),
        Index("ix_budgets_user_month", "user_id", "month"),
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
        Index("ix_categories_user_name", "user_id", "name"),
    )
