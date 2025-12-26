from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callbacks import AdminCallback


def brands_list_keyboard(category_id: int, brands):
    keyboard = []

    if brands:
        for brand in brands:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🗑 {brand.name}",
                    callback_data=AdminCallback(
                        action="brand_delete",
                        value=str(brand.id),
                        role='admin'
                    ).pack()
                )
            ])
    else:
        keyboard.append([
            InlineKeyboardButton(
                text="(брендов нет)",
                callback_data="noop",
                role='admin'
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="➕ Добавить бренд",
            callback_data=AdminCallback(
                action="brand_create",
                value=str(category_id),
                role='admin'
            ).pack()
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data=AdminCallback(
                action="subcategory_list",
                value=str(category_id),
                role='admin'
            ).pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
