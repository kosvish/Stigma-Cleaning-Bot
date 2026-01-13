from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callbacks import ExpenseCallback, AdminCallback  # Убедись, что AdminCallback импортирован


# 1. Выбор типа (Назад -> в главное меню)
def expense_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Прямой", callback_data="expense_type:direct"),
            InlineKeyboardButton(text="Общий", callback_data="expense_type:general")
        ],
        [
            # Возврат в админку или менеджерскую (зависит от логики, тут пример для админа)
            InlineKeyboardButton(
                text="⬅️ Отмена",
                callback_data=AdminCallback(action="back", role='admin').pack()
            )
        ]
    ])


# 2. Категории (Назад -> к выбору типа)
def expense_categories_keyboard(categories):
    keyboard = []
    for cat in categories:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📂 {cat.name}",
                callback_data=ExpenseCallback(action="expense_category_select", value=str(cat.id)).pack()
            )
        ])

    # КНОПКА НАЗАД
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=ExpenseCallback(action="back_to_type").pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# 3. Подкатегории (Назад -> к категориям)
def expense_subcategories_keyboard(subcategories):
    keyboard = []
    for sub in subcategories:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📁 {sub.name}",
                callback_data=ExpenseCallback(action="expense_subcategory_select", value=str(sub.id)).pack()
            )
        ])

    # КНОПКА НАЗАД
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=ExpenseCallback(action="back_to_categories").pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# 4. Бренды (Назад -> к подкатегориям)
def expense_brands_keyboard(brands):
    keyboard = []
    for brand in brands:
        keyboard.append([
            InlineKeyboardButton(
                text=brand.name,
                callback_data=ExpenseCallback(action="expense_brand_select", brand_id=brand.id, value=brand.name).pack()
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            text='Нету бренда',
            callback_data=ExpenseCallback(action="expense_brand_select", value='--').pack()
        )
    ])

    # КНОПКА НАЗАД
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=ExpenseCallback(action="back_to_subcategories").pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# 5. ID Заказов (Назад -> к вводу цены)
def expense_order_ids_keyboard(order_ids: list[str]) -> InlineKeyboardMarkup:
    keyboard = []
    for oid in order_ids:
        keyboard.append([
            InlineKeyboardButton(
                text=oid,
                callback_data=ExpenseCallback(action="expense_set_order", value=oid).pack()
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            text="Пропустить / Нет заказов",
            callback_data=ExpenseCallback(action="expense_set_order", value="-").pack()
        )
    ])

    # КНОПКА НАЗАД
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад к цене",
            callback_data=ExpenseCallback(action="back_to_cost").pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# 6. Города (Назад -> к выбору заказа)
def expense_cities_keyboard(cities):
    keyboard = []
    for city in cities:
        keyboard.append([
            InlineKeyboardButton(
                text=city.name,
                callback_data=ExpenseCallback(action="expense_set_city", value=str(city.name)).pack()
            )
        ])

    # КНОПКА НАЗАД
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад к заказам",
            callback_data=ExpenseCallback(action="back_to_orders").pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Хелпер для ручного ввода (оставляем как в прошлом ответе)
def back_button_keyboard(target_action: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=ExpenseCallback(action=target_action).pack())]
    ])


def expense_confirm_keyboard(state_data: dict) -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения расхода:
    - Верхняя кнопка: ✅ Подтвердить
    - Ниже: кнопки для редактирования полей
    """
    keyboard = []

    # ✅ Подтверждение
    keyboard.append([
        InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data=ExpenseCallback(action="confirm_expense", value='yes').pack()
        )
    ])

    # Поля для редактирования
    editable_fields = [
        ("cost", "Стоимость"),
        ("quantity", "Кол-во"),
        ("category", "Категория"),
        ("subcategory", "Подкатегория"),
        ("brand", "Бренд"),
        ("name", "Наименование"),
        ("order", "ID заказа"),
        ("city", "Город")
    ]

    for field_key, field_label in editable_fields:
        if field_key in state_data:
            display_value = state_data[field_key]
            keyboard.append([
                InlineKeyboardButton(

                    text=f"{field_label}: {display_value}",
                    callback_data=ExpenseCallback(action=f"edit_{field_key}").pack()
                )
            ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
