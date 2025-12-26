from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callbacks import AdminCallback, ExpenseCallback


def admin_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Управление пользователями",
                    callback_data=AdminCallback(action="users", role='admin').pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Управление категориями",
                    callback_data=AdminCallback(action="categories", role='admin').pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔐 Доступы и пароли",
                    callback_data=AdminCallback(action="access", role='admin').pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Записать расход",
                    callback_data=ExpenseCallback(action="expense_create").pack()
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
                    callback_data=AdminCallback(action="users_list", role='admin').pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Удалить пользователя",
                    callback_data=AdminCallback(action="users_delete", role='admin').pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=AdminCallback(action="back", role='admin').pack()
                )
            ]
        ]
    )