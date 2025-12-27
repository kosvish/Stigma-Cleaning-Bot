from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callbacks import AdminCallback
from app.database.models.user import User


def users_list_keyboard(users: list[User]):
    keyboard = []

    for user in users:
        keyboard.append([
            InlineKeyboardButton(
                text=f"👤 {user.full_name} ({user.role}) ({user.city})",
                callback_data=AdminCallback(
                    action="user_view",
                    user_id=user.telegram_id
                ).pack()
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=AdminCallback(action="back", role='admin').pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def user_actions_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=AdminCallback(
                        action="user_edit",
                        user_id=user_id
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=AdminCallback(
                        action="user_delete",
                        user_id=user_id
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=AdminCallback(action="users", role='admin').pack()
                )
            ]
        ]
    )


def user_edit_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏙 Сменить город",
                    callback_data=AdminCallback(
                        action="user_change_city",
                        user_id=user_id
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧩 Сменить роль",
                    callback_data=AdminCallback(
                        action="user_change_role",
                        user_id=user_id
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=AdminCallback(
                        action="user_view",
                        user_id=user_id,
                        role='admin'
                    ).pack()
                )
            ]
        ]
    )

from app.utils.constants import CITIES

def user_city_keyboard(user_id: int):
    keyboard = []

    for city in CITIES:
        keyboard.append([
            InlineKeyboardButton(
                text=city,
                callback_data=AdminCallback(
                    action="user_set_city",
                    user_id=user_id,
                    value=city
                ).pack()
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=AdminCallback(
                action="user_edit",
                user_id=user_id,
                role='admin'
            ).pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


from app.utils.constants import ROLES

def user_role_keyboard(user_id: int):
    keyboard = []

    for role in ROLES:
        keyboard.append([
            InlineKeyboardButton(
                text=role,
                callback_data=AdminCallback(
                    action="user_set_role",
                    user_id=user_id,
                    value=role
                ).pack()
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=AdminCallback(
                action="user_edit",
                user_id=user_id,
                role='admin'
            ).pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
