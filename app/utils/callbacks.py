from aiogram.filters.callback_data import CallbackData


class AdminCallback(CallbackData, prefix="admin"):
    action: str
    user_id: int | None = None
    value: str | None = None
    role: str | None = 'admin'


class ExpenseCallback(CallbackData, prefix="expense"):
    action: str
    category_id: int | None = None
    subcategory_id: int | None = None
    brand_id: int | None = None
    value: str | None = None


def is_admin_or_manager(callback_data: AdminCallback):
    return callback_data.role in ["admin", "manager"]
