from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callbacks import AdminCallback


def categories_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📦 Категории расходов",
            callback_data=AdminCallback(action="category_list", role='admin').pack()
        )],
        [InlineKeyboardButton(
            text="⬅ Назад",
            callback_data=AdminCallback(action="back", role='admin').pack()
        )]
    ])


def categories_list_keyboard(categories):
    keyboard = []

    for cat in categories:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📂 {cat.name}",
                callback_data=AdminCallback(
                    action="subcategory_list",
                    value=str(cat.id),
                    role='admin'
                ).pack()
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="➕ Создать категорию",
            callback_data=AdminCallback(action="category_create", role='admin').pack()
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data=AdminCallback(action="back", role='admin').pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)