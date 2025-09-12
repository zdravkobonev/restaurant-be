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
        # Clear existing user-role associations and remove old roles
        # We do not modify schema; we detach roles from users and delete Role rows.
        users = db.scalars(select(User)).all()
        for u in users:
            if u.roles:
                u.roles = []
                db.add(u)
        db.flush()

        # delete all existing roles
        existing_roles = db.scalars(select(Role)).all()
        for r in existing_roles:
            db.delete(r)
        db.flush()

        def get_or_create_role(name, parent=None):
            # create a role with optional parent (parent can be Role or id)
            r = db.scalar(select(Role).where(Role.name == name))
            if r:
                return r

            if isinstance(parent, int):
                r = Role(name=name, parent_id=parent)
            elif parent is None:
                r = Role(name=name)
            else:
                r = Role(name=name, parent=parent)

            db.add(r)
            db.flush()
            return r

        # New roles and sub-roles as requested
        # Маркиране
        m = get_or_create_role("Маркиране")
        m_mark = get_or_create_role("маркиране", parent=m.id)
        m_pay = get_or_create_role("приемане на плащания", parent=m.id)
        m_open = get_or_create_role("откриване на сметка", parent=m.id)
        m_close = get_or_create_role("закриване на сметка", parent=m.id)
        m_void = get_or_create_role("сторниране", parent=m.id)

        # Конфигурация
        cfg = get_or_create_role("Конфигурация")
        cfg_menu = get_or_create_role("конфигурации на меню", parent=cfg.id)
        cfg_sys = get_or_create_role("системна конфигурация", parent=cfg.id)

        # Монитори
        monitors = get_or_create_role("Монитори")
        mon_bar = get_or_create_role("монитор на бар", parent=monitors.id)
        mon_kitchen = get_or_create_role("монитор на кухня", parent=monitors.id)
        mon_deliveries = get_or_create_role("монитор на доставки", parent=monitors.id)

        # Справки
        reports = get_or_create_role("Справки")
        rep_sales = get_or_create_role("отчет продажби", parent=reports.id)
        rep_payments = get_or_create_role("отчет за плащания", parent=reports.id)
        rep_items = get_or_create_role("отчет за артикули", parent=reports.id)
        rep_staff = get_or_create_role("отчет за служители", parent=reports.id)

        # Резервации
        reservations = get_or_create_role("Резервации")
        res_create = get_or_create_role("създаване на резервация", parent=reservations.id)
        res_view = get_or_create_role("преглед на резервации", parent=reservations.id)

        # Складова база
        warehouse = get_or_create_role("Складова база")
        wh_receive = get_or_create_role("приемане на стока", parent=warehouse.id)
        wh_view = get_or_create_role("преглед на наличности", parent=warehouse.id)

        # Доставки
        deliveries = get_or_create_role("Доставки")
        del_create = get_or_create_role("създаване на доставка", parent=deliveries.id)
        del_view = get_or_create_role("преглед на доставки", parent=deliveries.id)

        # Отстъпки
        discounts = get_or_create_role("Отстъпки")
        disc_create = get_or_create_role("създаване на отстъпка", parent=discounts.id)
        disc_view = get_or_create_role("преглед на отстъпки", parent=discounts.id)

        # Determine role to grant to admin: choose first top-level group's first child
        assigned_role = m_mark

        user = db.scalar(select(User).where(User.username == username))
        if user:
            # update existing user's roles
            user.roles = [assigned_role]
            # update password only if ADMIN_PASSWORD env provided
            if os.getenv("ADMIN_PASSWORD"):
                user.password_hash = hash_password(password)
            db.add(user)
            db.commit()
            print(f"User '{username}' exists — roles updated to '{assigned_role.name}'.")
            return

        # Create new admin user and assign role
        user = User(username=username, password_hash=hash_password(password))
        user.roles.append(assigned_role)
        db.add(user)
        db.commit()
        print(f"User '{username}' created with role '{assigned_role.name}'.")

if __name__ == "__main__":
    main()
