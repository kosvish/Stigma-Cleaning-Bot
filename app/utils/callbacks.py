from aiogram.filters.callback_data import CallbackData


class AdminCallback(CallbackData, prefix="admin"):
    action: str
    user_id: int | None = None
    value: str | None = None