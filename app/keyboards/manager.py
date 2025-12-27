from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callbacks import AdminCallback, ExpenseCallback


def manager_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Записать расход",
                    callback_data=ExpenseCallback(action="expense_create").pack()
                )
            ]
        ]
    )