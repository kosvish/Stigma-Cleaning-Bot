from app.database.session import SessionLocal
from app.database.models.expense_subcategory import ExpenseSubCategory


def get_subcategories_by_category(category_id: int):
    with SessionLocal() as session:
        return (
            session.query(ExpenseSubCategory)
            .filter_by(category_id=category_id)
            .order_by(ExpenseSubCategory.name)
            .all()
        )


def create_subcategory(category_id: int, name: str) -> bool:
    with SessionLocal() as session:
        exists = (
            session.query(ExpenseSubCategory)
            .filter_by(category_id=category_id, name=name)
            .first()
        )
        if exists:
            return False

        sub = ExpenseSubCategory(
            name=name,
            category_id=category_id
        )
        session.add(sub)
        session.commit()
        return True


def delete_subcategory(subcategory_id: int) -> bool:
    with SessionLocal() as session:
        sub = session.get(ExpenseSubCategory, subcategory_id)
        if not sub:
            return False

        session.delete(sub)
        session.commit()
        return True
