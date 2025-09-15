import getpass
import os
from sqlalchemy import select
from sqlalchemy.orm import Session

# позволяваме стартиране от корен на проекта
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db import engine
from app.models import User, Role
from app.security import hash_password
from sqlalchemy import select

def main():
    username = os.getenv("ADMIN_USERNAME") or input("Admin username [admin]: ") or "admin"
    password = os.getenv("ADMIN_PASSWORD") or getpass.getpass("Admin password: ")

    with Session(engine) as db:
        # Idempotent seed: do not delete existing roles or user-role relations.
        # Instead, ensure each default role exists and create it if missing.

        def get_or_create_role(name, parent=None):
            # create a role with optional parent (parent can be Role or id)
            r = db.scalar(select(Role).where(Role.name == name))
            if r:
                return r

            pid = None
            if isinstance(parent, int):
                pid = parent
            elif parent is not None and hasattr(parent, "id"):
                pid = parent.id

            r = Role(name=name, parent_id=pid)
            db.add(r)
            db.flush()
            return r

        # Deterministic role spec: (expected_id, name, parent_expected_id)
        roles_spec = [
            (1, "Маркиране", None),
            (2, "маркиране", 1),
            (3, "приемане на плащания", 1),
            (4, "откриване на сметка", 1),
            (5, "закриване на сметка", 1),
            (6, "сторниране", 1),

            (7, "Конфигурация", None),
            (8, "конфигурации на меню", 7),
            (9, "системна конфигурация", 7),

            (10, "Монитори", None),
            (11, "монитор на бар", 10),
            (12, "монитор на кухня", 10),
            (13, "монитор на доставки", 10),

            (14, "Справки", None),
            (15, "отчет продажби", 14),
            (16, "отчет за плащания", 14),
            (17, "отчет за артикули", 14),
            (18, "отчет за служители", 14),

            (19, "Резервации", None),
            (20, "създаване на резервация", 19),
            (21, "преглед на резервации", 19),

            (22, "Складова база", None),
            (23, "приемане на стока", 22),
            (24, "преглед на наличности", 22),

            (25, "Доставки", None),
            (26, "създаване на доставка", 25),
            (27, "преглед на доставки", 25),

            (28, "Отстъпки", None),
            (29, "създаване на отстъпка", 28),
            (30, "преглед на отстъпки", 28),
        ]

        # Create roles in order, trying to assign expected id when available and free.
        created_roles = {}
        for expected_id, name, parent_expected in roles_spec:
            # if role with this name exists -> keep it
            existing = db.scalar(select(Role).where(Role.name == name))
            if existing:
                created_roles[expected_id] = existing
                continue

            # ensure parent exists and resolve its id
            parent_id = None
            if parent_expected is not None:
                # parent should have been created earlier in the loop
                parent = created_roles.get(parent_expected) or db.scalar(select(Role).where(Role.id == parent_expected))
                if parent:
                    parent_id = parent.id

            # check if expected_id is free
            id_taken = db.scalar(select(Role).where(Role.id == expected_id))
            if id_taken:
                # cannot force id, create normally
                r = Role(name=name, parent_id=parent_id)
            else:
                r = Role(id=expected_id, name=name, parent_id=parent_id)

            db.add(r)
            db.flush()
            created_roles[expected_id] = r

        # Assign to admin all roles that are child roles (parent_id is not NULL)
        # First, ensure all roles have been created by the get_or_create_role calls above.

        # fetch all roles that are children (parent_id not null)
        child_roles = db.scalars(select(Role).where(Role.parent_id.isnot(None))).all()

        user = db.scalar(select(User).where(User.username == username))
        if user:
            # append any missing child roles to existing user
            existing_role_ids = {r.id for r in (user.roles or [])}
            for r in child_roles:
                if r.id not in existing_role_ids:
                    user.roles.append(r)
            # update password only if ADMIN_PASSWORD env provided
            if os.getenv("ADMIN_PASSWORD"):
                user.password_hash = hash_password(password)
            db.add(user)
            db.commit()
            print(f"User '{username}' exists — ensured {len(child_roles)} child roles assigned.")
            return

        # Create new admin user and assign all child roles
        user = User(username=username, password_hash=hash_password(password))
        for r in child_roles:
            user.roles.append(r)
        db.add(user)
        db.commit()
        print(f"User '{username}' created with {len(child_roles)} child roles assigned.")

if __name__ == "__main__":
    main()
