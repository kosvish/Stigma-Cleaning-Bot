from app.database.models.city import City
from app.database.session import SessionLocal


def get_all_cities():
    with SessionLocal() as session:
        return session.query(City).all()


def add_city(name: str):
    db = SessionLocal()
    try:
        city = City(name=name)
        db.add(city)
        db.commit()
    finally:
        db.close()

def delete_city(city_id: int):

    db = SessionLocal()
    try:
        db.query(City).filter(City.id == city_id).delete()
        db.commit()
    finally:
        db.close()