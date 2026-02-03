from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callbacks import AdminCallback, ExpenseCallback, CalcCallback


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
                    text="🏙️ Города",
                    callback_data=AdminCallback(action="city", role='admin').pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Записать расход",
                    callback_data=ExpenseCallback(action="expense_create").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧮 Рассчитать уборку",
                    callback_data=CalcCallback(action="start").pack()
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


def city_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📋 Список городов",
                callback_data=AdminCallback(action="city_list", role='admin').pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="➕ Добавить город",
                callback_data=AdminCallback(action="city_add", role='admin').pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅ Назад",
                callback_data=AdminCallback(action="back", role='admin').pack()
            )
        ]
    ])


def cities_list_keyboard(cities):
    keyboard = []

    for city in cities:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🏙 {city.name}",
                callback_data=AdminCallback(
                    action="city_delete",
                    value=str(city.id),
                    role='admin'
                ).pack()
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data=AdminCallback(action="city", role='admin').pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
