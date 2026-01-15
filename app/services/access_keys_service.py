from app.config import GLOBAL_PASSWORD
from app.database.session import SessionLocal
from app.database.models.access_key import AccessKey
from app.utils.security import verify_password


def get_all_keys():
    with SessionLocal() as session:
        return session.query(AccessKey).all()


def create_access_key(password: str, role: str):
    with SessionLocal() as session:
        key = AccessKey(
            password=password,
            role=role,
            is_active=True,
            used_count=0
        )
        session.add(key)
        session.commit()
        return key


def delete_key(key_id: int):
    with SessionLocal() as session:
        key = session.query(AccessKey).filter(AccessKey.id == key_id).first()
        if not key:
            return False
        session.query(AccessKey).filter(AccessKey.id == key_id).delete()
        session.commit()
        return True


def get_key_by_password(password_input: str):
    session = SessionLocal()
    try:
        # Получаем все ключи (или фильтруем активные)
        keys = session.query(AccessKey).all()

        for key in keys:
            # Сравниваем хеши (или просто строки, если у тебя нет хеширования)
            # Если используешь verify_password из utils/security.py:
            print(key.password)
            if verify_password(password_input, key.password):
                return True
        if password_input == GLOBAL_PASSWORD:
            return True
        return None
    finally:
        session.close()
