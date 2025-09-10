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

def main():
    username = os.getenv("ADMIN_USERNAME") or input("Admin username [admin]: ") or "admin"
    password = os.getenv("ADMIN_PASSWORD") or getpass.getpass("Admin password: ")

    with Session(engine) as db:
        exists = db.scalar(select(User).where(User.username == username))
        if exists:
            print(f"User '{username}' already exists. Nothing to do.")
            return

        # Seed roles if they don't exist
        def get_or_create_role(name, parent=None):
            """Create or return a Role. `parent` may be None, a Role instance, or an int id.
            We handle each case safely to avoid passing wrong types to SQLAlchemy relationships.
            """
            r = db.scalar(select(Role).where(Role.name == name))
            if r:
                return r

            if isinstance(parent, int):
                r = Role(name=name, parent_id=parent)
            elif parent is None:
                r = Role(name=name)
            else:
                # assume parent is a Role instance
                r = Role(name=name, parent=parent)

            db.add(r)
            db.flush()
            return r

        # Main roles and subroles per request
        # Управител на заведение -> подрола: всеобщо (всичко)
        manager_role = get_or_create_role("Управител на заведение")
        manager_sub = get_or_create_role("Управител: всичко", parent=manager_role.id)

        # Сервитьор -> подроли: всички, сервитьор, резервации
        waiter_role = get_or_create_role("Сервитьор")
        waiter_sub_all = get_or_create_role("Сервитьор: всички", parent=waiter_role.id)
        waiter_sub_waiter = get_or_create_role("Сервитьор: сервитьор", parent=waiter_role.id)
        waiter_sub_res = get_or_create_role("Сервитьор: резервации", parent=waiter_role.id)

        # Счетоводител, монитор, складов достъп -> подрола: всичко
        acc_role = get_or_create_role("Счетоводител")
        acc_sub = get_or_create_role("Счетоводител: всичко", parent=acc_role.id)

        monitor_role = get_or_create_role("Монитор")
        monitor_sub = get_or_create_role("Монитор: всичко", parent=monitor_role.id)

        warehouse_role = get_or_create_role("Скaладов достъп")
        warehouse_sub = get_or_create_role("Скaладов достъп: всичко", parent=warehouse_role.id)

        # Create user and assign highest role (manager) by default
        user = User(username=username, password_hash=hash_password(password))
        user.roles.append(manager_sub)
        db.add(user)
        db.commit()
        print(f"User '{username}' created with role '{manager_sub.name}'.")

if __name__ == "__main__":
    main()
