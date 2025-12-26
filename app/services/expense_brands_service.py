from app.database.session import SessionLocal
from app.database.models.expense_brand import ExpenseBrand


def get_brands_by_category(category_id: int):
    with SessionLocal() as session:
        return (
            session.query(ExpenseBrand)
            .filter_by(category_id=category_id)
            .order_by(ExpenseBrand.name)
            .all()
        )


def create_brand(category_id: int, name: str) -> bool:
    with SessionLocal() as session:
        exists = (
            session.query(ExpenseBrand)
            .filter_by(category_id=category_id, name=name)
            .first()
        )
        if exists:
            return False

        brand = ExpenseBrand(
            name=name,
            category_id=category_id
        )
        session.add(brand)
        session.commit()
        return True


def delete_brand(brand_id: int) -> bool:
    with SessionLocal() as session:
        brand = session.get(ExpenseBrand, brand_id)
        if not brand:
            return False

        session.delete(brand)
        session.commit()
        return True