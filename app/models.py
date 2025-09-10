from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, String, DateTime, func, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


# Association table for many-to-many User <-> Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    failed_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Roles assigned to this user (many-to-many)
    roles: Mapped[List["Role"]] = relationship("Role", secondary=user_roles, back_populates="users")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)

    # children sub-roles
    children: Mapped[List["Role"]] = relationship("Role", backref="parent", remote_side=[id])

    # users that have this role
    users: Mapped[List[User]] = relationship("User", secondary=user_roles, back_populates="roles")
