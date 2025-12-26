from datetime import datetime

import pytz
from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.create_expense import expense_categories_keyboard, expense_subcategories_keyboard, \
    expense_brands_keyboard, expense_order_ids_keyboard, expense_cities_keyboard, expense_confirm_keyboard
from app.services.cities_service import get_all_cities
from app.services.expense_brands_service import get_brands_by_category
from app.services.expense_categories_service import get_all_categories, get_category_by_id
from app.services.expense_create import expense_type_keyboard
from app.services.expense_subcategories_service import get_subcategories_by_category, get_subcategories_by_id
from app.services.google_sheets_service import get_recent_order_ids, append_expense_to_sheet
from app.states.create_expense import CreateExpenseFSM
from app.utils.callbacks import AdminCallback, ExpenseCallback
from app.utils.text import format_expense_preview

router = Router()


@router.callback_query(ExpenseCallback.filter(F.action == "expense_create"))
async def expense_create_start(call: CallbackQuery, callback_data: AdminCallback, state: FSMContext):
    # Сохраняем роль пользователя в state (можно использовать для логики)
    # await state.update_data(user_role=callback_data.role)

    await call.message.edit_text(
        "💰 <b>Создание расхода</b>\n\n"
        "Выберите тип расхода:",
        reply_markup=expense_type_keyboard(),  # inline кнопки "Прямой" и "Общий"
        parse_mode="HTML"
    )

    await state.set_state(CreateExpenseFSM.waiting_for_type)
    await call.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("expense_type:"))
async def expense_type_selected(call: CallbackQuery, state: FSMContext):
    expense_type = call.data.split(":")[1]  # direct / general
    expense_value = call.data.split(":")[2]  # direct / general
    categories = get_all_categories()
    await state.update_data(expense_type=expense_type)
    await state.update_data(expense_value=expense_value)

    # Переходим к выбору категории
    await call.message.edit_text(
        "🏷 Выберите категорию расхода:",
        reply_markup=expense_categories_keyboard(categories),  # inline кнопки категорий из БД
        parse_mode="HTML"
    )

    await state.set_state(CreateExpenseFSM.waiting_for_category)
    await call.answer()


@router.callback_query(ExpenseCallback.filter(F.action == "expense_category_select"))
async def expense_category_selected(call: CallbackQuery, callback_data: ExpenseCallback, state: FSMContext):
    category_id = int(callback_data.value)
    category = get_category_by_id(category_id)
    await state.update_data(category_id=category_id)
    await state.update_data(category=category.name)

    # # Здесь мы можем получить подкатегории из БД по выбранной категории
    subcategories = get_subcategories_by_category(category_id)

    await call.message.edit_text(
        "📁 Выберите подкатегорию:",
        reply_markup=expense_subcategories_keyboard(subcategories),
        parse_mode="HTML"
    )

    await state.set_state(CreateExpenseFSM.waiting_for_subcategory)
    await call.answer()


@router.callback_query(ExpenseCallback.filter(F.action == "expense_subcategory_select"))
async def expense_subcategory_selected(call: CallbackQuery, callback_data: ExpenseCallback, state: FSMContext):
    subcategory_id = int(callback_data.value)
    subcategory = get_subcategories_by_id(subcategory_id)
    await state.update_data(subcategory_id=subcategory_id, subcategory=subcategory.name)

    # Получаем бренды по категории, если нужно
    data = await state.get_data()
    category_id = data.get("category_id")
    brands = get_brands_by_category(category_id)

    await call.message.edit_text(
        "🏷 Выберите бренд:",
        reply_markup=expense_brands_keyboard(brands),
        parse_mode="HTML"
    )

    await state.set_state(CreateExpenseFSM.waiting_for_brand)
    await call.answer()


@router.callback_query(ExpenseCallback.filter(F.action == "expense_brand_select"))
async def expense_brand_selected(call: CallbackQuery, callback_data: ExpenseCallback, state: FSMContext):
    if callback_data.value.isnumeric():
        brand_id = int(callback_data.value)
        brand = get_brands_by_category(brand_id)
        await state.update_data(brand_id=brand_id, brand=brand.name)
    else:
        brand_id = 0
        await state.update_data(brand_id=brand_id, brand='-')

    await call.message.edit_text(
        "🔢 Введите количество едениц покупки или траты (например, 3):",
        parse_mode="HTML"
    )

    await state.set_state(CreateExpenseFSM.waiting_for_quantity)
    await call.answer()


@router.message(CreateExpenseFSM.waiting_for_quantity)
async def expense_quantity_input(message: types.Message, state: FSMContext):
    try:
        quantity = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число.")
        return

    await state.update_data(quantity=quantity)

    await message.answer("✏️ Введите наименование расхода (назначение):")
    await state.set_state(CreateExpenseFSM.waiting_for_name)


@router.message(CreateExpenseFSM.waiting_for_name)
async def expense_name_input(message: types.Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)

    await message.answer("💰 Введите стоимость расхода:")
    await state.set_state(CreateExpenseFSM.waiting_for_cost)


# --- FSM handler для ввода стоимости ---
@router.message(CreateExpenseFSM.waiting_for_cost)
async def expense_price_input(message: types.Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число.")
        return

    await state.update_data(cost=price)

    # Получаем последние ID заказов через Google Apps Script
    recent_order_ids = get_recent_order_ids(days=3)

    await message.answer(
        "🔗 Выберите ID заказа (или нажмите Пропустить / Нет заказов):",
        reply_markup=expense_order_ids_keyboard(recent_order_ids)
    )

    # Переходим к следующему состоянию FSM
    await state.set_state(CreateExpenseFSM.waiting_for_order_id)


@router.callback_query(ExpenseCallback.filter(F.action == "expense_set_order"))
async def expense_order_selected(
    call: CallbackQuery,
    callback_data: ExpenseCallback,
    state: FSMContext
):
    order_id = callback_data.value if callback_data.value != "none" else None
    await state.update_data(order_id=order_id)

    cities = get_all_cities()

    await call.message.edit_text(
        "🏙 Выберите город:",
        reply_markup=expense_cities_keyboard(cities)
    )

    await state.set_state(CreateExpenseFSM.waiting_for_city)
    await call.answer()




@router.callback_query(ExpenseCallback.filter(F.action == "expense_set_city"), CreateExpenseFSM.waiting_for_city)
async def expense_city_selected(call: CallbackQuery, callback_data: ExpenseCallback, state: FSMContext):
    await state.update_data(city=callback_data.value)

    data = await state.get_data()
    # data["date"] = datetime.now().strftime("%d.%m.%Y")  # Добавляем текущую дату
    date = datetime.now().strftime("%d.%m.%Y")
    await state.update_data(date=date)
    await call.message.edit_text(
        "💡 Проверьте введённые данные:",
        reply_markup=expense_confirm_keyboard(data),
        parse_mode="HTML"
    )

    await state.set_state(CreateExpenseFSM.waiting_for_confirm)
    await call.answer()




@router.callback_query(ExpenseCallback.filter(F.action == "confirm_expense"), CreateExpenseFSM.waiting_for_confirm)
async def expense_confirm(call: CallbackQuery, callback_data: ExpenseCallback, state: FSMContext):
    """
    Универсальный обработчик подтверждения расхода.
    """
    data = await state.get_data()

    if callback_data.value == "yes":
        # Пользователь подтвердил расход, записываем в Google Sheet
        append_expense_to_sheet(data)

        await call.message.edit_text(
            "✅ Расход успешно записан!",
        )
        await state.clear()
        await call.answer()
        return

    elif callback_data.value.startswith("edit_"):
        # Пользователь хочет редактировать одно из полей
        # Например edit_cost, edit_quantity, edit_name, edit_category и т.д.
        field_to_edit = callback_data.value.replace("edit_", "")
        edit_handlers_map = {
            "cost": CreateExpenseFSM.waiting_for_cost,
            "quantity": CreateExpenseFSM.waiting_for_quantity,
            "name": CreateExpenseFSM.waiting_for_name,
            "category": CreateExpenseFSM.waiting_for_category,
            "subcategory": CreateExpenseFSM.waiting_for_subcategory,
            "brand": CreateExpenseFSM.waiting_for_brand,
            "order_id": CreateExpenseFSM.waiting_for_order_id,
            "city": CreateExpenseFSM.waiting_for_city
        }

        next_state = edit_handlers_map.get(field_to_edit)
        if next_state:
            await state.set_state(next_state)
        await call.answer()
        return

    # Если callback не распознан, просто обновляем превью
    await call.message.edit_text(
        "💡 Проверьте введённые данные:",
        reply_markup=expense_confirm_keyboard(data),
        parse_mode="HTML"
    )
    await call.answer()



