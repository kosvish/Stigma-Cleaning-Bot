from app.database.session import SessionLocal
from app.database.models.user import User


def get_all_users():
    with SessionLocal() as session:
        return session.query(User).all()


def get_user_by_id(user_id: int):
    with SessionLocal() as session:
        return session.query(User).filter(User.telegram_id == user_id).first()


def delete_user(user_id: int):
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
            return True
        return False


def update_user_city(user_id: int, city: str):
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            return False

        user.city = city
        session.commit()
        return True


def update_user_role(user_id: int, role: str):
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            return False

        user.role = role
        session.commit()
        return True
