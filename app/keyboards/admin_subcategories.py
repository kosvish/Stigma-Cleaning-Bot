from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callbacks import AdminCallback


def subcategories_list_keyboard(category_id: int, category_name: str, subcategories):
    keyboard = []

    if subcategories:
        for sub in subcategories:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🗑 {sub.name}",
                    callback_data=AdminCallback(
                        action="subcategory_delete",
                        value=str(sub.id)
                    ).pack()
                )
            ])
    else:
        keyboard.append([
            InlineKeyboardButton(
                text="(нет подкатегорий)",
                callback_data="noop"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="➕ Добавить подкатегорию",
            callback_data=AdminCallback(
                action="subcategory_create",
                value=str(category_id),
                role='admin'
            ).pack()
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            text="📦 Бренды",
            callback_data=AdminCallback(
                action="brand_list",
                value=str(category_id),
                role='admin'
            ).pack()
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            text="🗑 Удалить категорию",
            callback_data=AdminCallback(
                action="category_delete",
                value=str(category_id),
                role='admin'
            ).pack()
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data=AdminCallback(
                action="category_list",
                role='admin'
            ).pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
