from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callbacks import AdminCallback


def admin_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Управление пользователями",
                    callback_data=AdminCallback(action="users").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Управление категориями",
                    callback_data=AdminCallback(action="categories").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔐 Доступы и пароли",
                    callback_data=AdminCallback(action="access").pack()
                )
            ]
        ]
    )


def admin_users_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Активные пользователи",
                    callback_data=AdminCallback(action="users_list").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Удалить пользователя",
                    callback_data=AdminCallback(action="users_delete").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=AdminCallback(action="back").pack()
                )
            ]
        ]
    )