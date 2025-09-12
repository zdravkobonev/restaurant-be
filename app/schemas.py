from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional


class LoginIn(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=6, max_length=128)


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    roles: List[str] = []


# Roles
class RoleOut(BaseModel):
    id: int
    name: str


class RoleNestedOut(RoleOut):
    children: List["RoleNestedOut"] = []


# Users
class UserOut(BaseModel):
    id: int
    username: str
    roles: List[str] = []


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=6, max_length=128)
    # roles passed as list of role ids
    roles: Optional[List[int]] = None


class UserUpdateRoles(BaseModel):
    # allow updating roles only (list of role ids)
    roles: Optional[List[int]] = None


# Pydantic forward refs
RoleNestedOut.update_forward_refs()

