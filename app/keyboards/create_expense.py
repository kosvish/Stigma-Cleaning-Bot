from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.utils.callbacks import ExpenseCallback


def expense_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Прямой",
                callback_data="expense_type:direct"
            ),
            InlineKeyboardButton(
                text="Общий",
                callback_data="expense_type:general"
            )
        ]
    ])


def expense_categories_keyboard(categories):
    """
    Создает inline-клавиатуру с категориями для записи расхода.
    categories - список объектов категорий из БД.
    """
    keyboard = []

    for cat in categories:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📂 {cat.name}",
                callback_data=ExpenseCallback(
                    action="expense_category_select",
                    value=str(cat.id)  # передаем id категории
                ).pack()
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def expense_subcategories_keyboard(subcategories):
    """
    Создает inline-клавиатуру с подкатегориями для выбора расхода.
    subcategories - список объектов подкатегорий из БД.
    """
    keyboard = []

    for sub in subcategories:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📁 {sub.name}",
                callback_data=ExpenseCallback(
                    action="expense_subcategory_select",
                    value=str(sub.id)
                ).pack()
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def expense_brands_keyboard(brands):
    keyboard = []

    for brand in brands:
        keyboard.append([
            InlineKeyboardButton(
                text=brand.name,
                callback_data=ExpenseCallback(
                    action="expense_brand_select",
                    brand_id=brand.id,
                    value=brand.name
                ).pack()
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            text='Нету бренда',
            callback_data=ExpenseCallback(
                action="expense_brand_select",
                value='--'
            ).pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def expense_order_ids_keyboard(order_ids: list[str]) -> InlineKeyboardMarkup:
    keyboard = []
    for oid in order_ids:
        keyboard.append([
            InlineKeyboardButton(
                text=oid,
                callback_data=ExpenseCallback(
                    action="expense_set_order",
                    value=oid
                ).pack()
            )
        ])
    # Кнопка "пропустить"
    keyboard.append([
        InlineKeyboardButton(
            text="Пропустить / Нет заказов",
            callback_data=ExpenseCallback(
                action="expense_set_order",
                value="-"
            ).pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def expense_cities_keyboard(cities):
    keyboard = []

    for city in cities:
        keyboard.append([
            InlineKeyboardButton(
                text=city.name,
                callback_data=ExpenseCallback(
                    action="expense_set_city",
                    value=str(city.name)
                ).pack()
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


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

