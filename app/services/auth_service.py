from app.database.session import SessionLocal
from app.database.models.access_key import AccessKey
from app.database.models.user import User
from app.utils.security import verify_password


def authenticate_user(telegram_id: int, username: str, full_name: str, password: str):
    with SessionLocal() as session:
        # Получаем все активные ключи доступа
        keys = session.query(AccessKey).filter(AccessKey.is_active == True).all()

        for key in keys:
            if verify_password(password, key.password):
                # Создаем пользователя, если пароль совпадает
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    full_name=full_name,
                    role=key.role
                )
                session.add(user)

                # Увеличиваем счетчик использования ключа
                key.used_count += 1

                session.commit()
                return user

        # Если пароль не совпал ни с одним ключом
        return None

def user_exists(telegram_id: int):
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            return True
        else:
            return False