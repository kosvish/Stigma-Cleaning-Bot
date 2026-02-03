from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def generate_categories_keyboard(categories_list, current_level_parent_id=None):
    builder = InlineKeyboardBuilder()

    for cat in categories_list:
        # В callback_data зашиваем ID категории и флаг, есть ли дети
        # Формат: cat_select:<id>:<has_children>
        has_child_flag = "1" if cat['has_children'] else "0"
        builder.button(
            text=cat['name'],
            callback_data=f"exp_cat:{cat['id']}:{has_child_flag}"
        )

    builder.adjust(2)  # По 2 кнопки в ряд

    # Кнопка "Назад", если мы внутри подкатегории
    if current_level_parent_id is not None:
        builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="exp_cat:back"))

    return builder.as_markup()