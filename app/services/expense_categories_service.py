from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.models.expense_category import ExpenseCategory


def get_all_categories():
    with SessionLocal() as session:
        return session.query(ExpenseCategory).order_by(ExpenseCategory.name).all()


def create_category(name: str) -> bool:
    with SessionLocal() as session:
        exists = session.query(ExpenseCategory).filter_by(name=name).first()
        if exists:
            return False

        category = ExpenseCategory(name=name)
        session.add(category)
        session.commit()
        return True


def delete_category(category_id: int) -> bool:
    with SessionLocal() as session:
        category = session.get(ExpenseCategory, category_id)
        if not category:
            return False

        session.delete(category)
        session.commit()
        return True


def get_category_by_id(category_id: int) -> ExpenseCategory | bool:
    with SessionLocal() as session:
        category = session.query(ExpenseCategory).filter_by(id=category_id).first()
        if category:
            return category
        else:
            return False
