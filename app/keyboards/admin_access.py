from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callbacks import AdminCallback
from app.utils.constants import ROLES


def admin_access_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Активные пароли",
                    callback_data=AdminCallback(action="access_list", role='admin').pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Создать пароль",
                    callback_data=AdminCallback(action="access_create", role='admin').pack()
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


def access_keys_list_keyboard(keys):
    keyboard = []

    for key in keys:
        status = "🟢" if key.is_active else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{status} {key.password} ({key.role})",
                callback_data=AdminCallback(
                    action="access_view",
                    value=str(key.id)
                ).pack()
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=AdminCallback(action="access",  role='admin').pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def access_key_actions_keyboard(key_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Удалить пароль",
                    callback_data=AdminCallback(
                        action="access_deactivate",
                        value=str(key_id),
                        role='admin'
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=AdminCallback(action="access_list", role='admin').pack()
                )
            ]
        ]
    )


def access_roles_keyboard(user_id: int):
    keyboard = []

    for role in ROLES:
        cb_data = AdminCallback(
            action="access_set_role",
            user_id=user_id,  # ✅ передаём user_id
            value=role,
            role='admin'
        ).pack()

        keyboard.append([
            InlineKeyboardButton(
                text=role,
                callback_data=cb_data,
                role='admin'
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
