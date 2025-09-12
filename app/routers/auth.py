from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import LoginIn, LoginOut, RoleLoginOut, RolesGroupedOut
from ..security import verify_password, create_access_token
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    # 1) Търсим потребителя
    user = db.scalar(select(User).where(User.username == payload.username))

    now = datetime.now(timezone.utc)
    if user and user.locked_until and user.locked_until > now:
        seconds_left = int((user.locked_until - now).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked. Try again in {seconds_left} seconds."
        )

    password_ok = False
    if user:
        password_ok = verify_password(payload.password, user.password_hash)

    if password_ok:
        # Успешен логин → нулираме failed_attempts + locked_until
        user.failed_attempts = 0
        user.locked_until = None
        db.add(user)
        db.commit()
        db.refresh(user)

        # Създаваме JWT
        access_token = create_access_token(data={"sub": user.username})
        # Build grouped roles: parent_id -> list of role ids
        grouped: dict[int | None, list[int]] = {}
        for r in (user.roles or []):
            pid = r.parent_id
            grouped.setdefault(pid, []).append(r.id)

        roles_grouped = [RolesGroupedOut(parentId=pid, roles=ids).dict() for pid, ids in grouped.items()]

        return {"access_token": access_token, "token_type": "bearer", "roles": roles_grouped}
    else:
        # Неуспешен логин
        if user:
            user.failed_attempts = (user.failed_attempts or 0) + 1
            if user.failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.failed_attempts = 0
                user.locked_until = now + timedelta(minutes=settings.LOCKOUT_MINUTES)
            db.add(user)
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )
