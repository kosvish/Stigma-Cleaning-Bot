from app.database.models.city import City
from app.database.session import SessionLocal


def get_all_cities():
    with SessionLocal() as session:
        return session.query(City).all()
