from aiogram.filters.callback_data import CallbackData


class AdminCallback(CallbackData, prefix="admin"):
    action: str
    user_id: int | None = None
    value: str | None = None
    role: str | None = None


class ExpenseCallback(CallbackData, prefix="expense"):
    action: str
    category_id: int | None = None
    subcategory_id: int | None = None
    brand_id: int | None = None
    value: str | None = None


class ManagerCallback(CallbackData, prefix="manager"):
    action: str
    category_id: int | None = None
    subcategory_id: int | None = None
    brand_id: int | None = None
    value: str | None = None
    role: str | None = 'manager'


class CalcCallback(CallbackData, prefix="calc"):
    action: str
    value: str = "none"
