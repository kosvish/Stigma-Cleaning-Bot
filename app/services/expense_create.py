from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.utils.callbacks import AdminCallback


def expense_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📦 Общий",
                callback_data="expense_type:general:Общий"
            ),
            InlineKeyboardButton(
                text="🎯 Прямой",
                callback_data="expense_type:direct:Прямой"
            ),
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=AdminCallback(action="back", role='admin').pack()
            )
        ]
    ])
