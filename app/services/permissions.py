from app.database.session import SessionLocal
from app.database.models.user import User


def user_has_role(telegram_id: int, allowed_roles: list[str]) -> bool:
    with SessionLocal() as session:
        user = session.query(User).filter(
            User.telegram_id == telegram_id
        ).first()

        if not user:
            return False

        return user.role in allowed_roles
