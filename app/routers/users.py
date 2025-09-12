from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Role, User
from ..schemas import RoleNestedOut, RoleOut, UserOut, UserCreate, UserUpdateRoles
from ..dependencies import get_current_user
from ..security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


def build_role_tree(roles: List[Role], parent_id=None) -> List[RoleNestedOut]:
    tree = []
    for r in [x for x in roles if (x.parent_id == parent_id)]:
        node = RoleNestedOut(id=r.id, name=r.name, children=build_role_tree(roles, r.id))
        tree.append(node)
    return tree


@router.get("/roles", response_model=List[RoleNestedOut])
def get_roles(db: Session = Depends(get_db), _=Depends(get_current_user)):
    roles = db.scalars(select(Role)).all()
    return build_role_tree(roles)


@router.get("/roles/flat", response_model=List[RoleOut])
def get_roles_flat(db: Session = Depends(get_db), _=Depends(get_current_user)):
    roles = db.scalars(select(Role)).all()
    return [RoleOut(id=r.id, name=r.name) for r in roles]


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(get_current_user)):
    users = db.scalars(select(User)).all()
    out = []
    for u in users:
        role_names = [r.name for r in (u.roles or [])]
        out.append(UserOut(id=u.id, username=u.username, roles=role_names))
    return out


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    # ensure username unique
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=payload.username, password_hash=hash_password(payload.password))

    # attach roles if provided
    if payload.roles:
        roles = db.scalars(select(Role).where(Role.id.in_(payload.roles))).all()
        user.roles = roles

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserOut(id=user.id, username=user.username, roles=[r.name for r in (user.roles or [])])


@router.put("/{user_id}", response_model=UserOut)
def update_user_roles(user_id: int, payload: UserUpdateRoles, db: Session = Depends(get_db), _=Depends(get_current_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.roles is not None:
        roles = db.scalars(select(Role).where(Role.id.in_(payload.roles))).all()
        user.roles = roles

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserOut(id=user.id, username=user.username, roles=[r.name for r in (user.roles or [])])


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return
