from app.database.session import SessionLocal
from app.database.models.access_key import AccessKey


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
