from datetime import datetime

import pytz
from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_main_keyboard
from app.keyboards.create_expense import expense_categories_keyboard, expense_subcategories_keyboard, \
    expense_brands_keyboard, expense_order_ids_keyboard, expense_cities_keyboard, back_button_keyboard, \
    expense_confirm_keyboard
from app.keyboards.manager import manager_main_keyboard
from app.services.cities_service import get_all_cities
from app.services.expense_brands_service import get_brands_by_category
from app.services.expense_categories_service import get_all_categories, get_category_by_id
from app.services.expense_create import expense_type_keyboard
from app.services.expense_subcategories_service import get_subcategories_by_category, get_subcategories_by_id
from app.services.google_sheets_service import get_recent_order_ids, append_expense_to_sheet
from app.services.permissions import user_has_role
from app.states.create_expense import CreateExpenseFSM
from app.utils.bot_message_utils import send_and_store, delete_prev_bot_message, delete_user_message
from app.utils.callbacks import AdminCallback, ExpenseCallback

router = Router()


# ==========================================
# БЛОК НАВИГАЦИИ "НАЗАД"
# ==========================================

@router.callback_query(ExpenseCallback.filter(F.action == "back_to_type"))
async def back_to_type(call: CallbackQuery, state: FSMContext):
    """Возврат от выбора категории к выбору типа"""
    await call.message.edit_text(
        "💰 <b>Создание расхода</b>\n\nВыберите тип расхода:",
        reply_markup=expense_type_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(CreateExpenseFSM.waiting_for_type)
    await call.answer()


@router.callback_query(ExpenseCallback.filter(F.action == "back_to_categories"))
async def back_to_categories(call: CallbackQuery, state: FSMContext):
    """Возврат от выбора подкатегории к списку категорий"""
    categories = get_all_categories()  # Заново получаем список

    await call.message.edit_text(
        "🏷 Выберите категорию расхода:",
        reply_markup=expense_categories_keyboard(categories),
        parse_mode="HTML"
    )
    await state.set_state(CreateExpenseFSM.waiting_for_category)
    await call.answer()


@router.callback_query(ExpenseCallback.filter(F.action == "back_to_subcategories"))
async def back_to_subcategories(call: CallbackQuery, state: FSMContext):
    """Возврат от выбора бренда к списку подкатегорий"""
    data = await state.get_data()
    category_id = data.get("category_id")  # Достаем ID категории из памяти

    subcategories = get_subcategories_by_category(category_id)

    await call.message.edit_text(
        "📁 Выберите подкатегорию:",
        reply_markup=expense_subcategories_keyboard(subcategories),
        parse_mode="HTML"
    )
    await state.set_state(CreateExpenseFSM.waiting_for_subcategory)
    await call.answer()


@router.callback_query(ExpenseCallback.filter(F.action == "back_to_brands"))
async def back_to_brands(call: CallbackQuery, state: FSMContext):
    """Возврат от ввода количества (ручной ввод) к списку брендов"""
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


@router.callback_query(ExpenseCallback.filter(F.action == "back_to_quantity"))
async def back_to_quantity(call: CallbackQuery, state: FSMContext):
    """Возврат от ввода имени к вводу количества"""
    await call.message.edit_text(
        "🔢 Введите количество едениц покупки или траты (например, 3):",
        reply_markup=back_button_keyboard("back_to_brands"),
        parse_mode="HTML"
    )
    await state.set_state(CreateExpenseFSM.waiting_for_quantity)
    await call.answer()


@router.callback_query(ExpenseCallback.filter(F.action == "back_to_name"))
async def back_to_name(call: CallbackQuery, state: FSMContext):
    """Возврат от ввода цены к вводу имени"""
    await call.message.edit_text(
        "✏️ Введите наименование расхода (назначение):",
        reply_markup=back_button_keyboard("back_to_quantity"),
        parse_mode="HTML"
    )
    await state.set_state(CreateExpenseFSM.waiting_for_name)
    await call.answer()


@router.callback_query(ExpenseCallback.filter(F.action == "back_to_cost"))
async def back_to_cost(call: CallbackQuery, state: FSMContext):
    """Возврат от выбора заказа к вводу цены"""
    await call.message.edit_text(
        "💰 Введите стоимость расхода:",
        reply_markup=back_button_keyboard("back_to_name"),
        parse_mode="HTML"
    )
    await state.set_state(CreateExpenseFSM.waiting_for_cost)
    await call.answer()


@router.callback_query(ExpenseCallback.filter(F.action == "back_to_orders"))
async def back_to_orders(call: CallbackQuery, state: FSMContext):
    """Возврат от выбора города к списку заказов"""
    # Тут есть нюанс: orders берутся из Google Sheets.
    # Чтобы не дергать Google лишний раз, лучше сохранить их в state при первом запросе,
    # но сейчас сделаем просто повторный запрос для надежности.

    recent_order_ids = get_recent_order_ids(days=3)

    await call.message.edit_text(
        "🔗 Выберите ID заказа (или нажмите Пропустить / Нет заказов):",
        reply_markup=expense_order_ids_keyboard(recent_order_ids),
        parse_mode="HTML"
    )
    await state.set_state(CreateExpenseFSM.waiting_for_order_id)
    await call.answer()


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
        brand_id = int(callback_data.brand_id)
        brands = get_brands_by_category(brand_id)
        index_brand = brands.index(brand_id)
        brand = brands[index_brand]
        await state.update_data(brand_id=brand_id, brand=brand.name)
    else:
        brand_id = 0
        await state.update_data(brand_id=brand_id, brand='-')

    await call.message.edit_text(
        "🔢 Введите количество едениц покупки или траты (например, 3):",
        parse_mode="HTML",
        reply_markup=back_button_keyboard("back_to_brands")
    )

    await state.set_state(CreateExpenseFSM.waiting_for_quantity)
    await call.answer()


@router.message(CreateExpenseFSM.waiting_for_quantity)
async def expense_quantity_input(message: types.Message, state: FSMContext):
    # 1. Удаляем сообщение пользователя (число, которое он ввел)
    await delete_user_message(message)

    try:
        quantity = float(message.text.replace(",", "."))
    except ValueError:
        # Если ошибка — отправляем временное сообщение и удаляем его через 3 сек (по желанию)
        msg = await message.answer("❌ Введите число!")
        # Можно тут ничего не делать, просто заставить ввести заново
        return

    # 2. Удаляем старый вопрос бота ("Введите количество...")
    await delete_prev_bot_message(message, state)

    await state.update_data(quantity=quantity)

    # 3. Отправляем новый вопрос и запоминаем его ID
    await send_and_store(
        message,
        state,
        "✏️ Введите наименование расхода (назначение):",
        reply_markup=back_button_keyboard("back_to_quantity")
    )
    await state.set_state(CreateExpenseFSM.waiting_for_name)


@router.message(CreateExpenseFSM.waiting_for_name)
async def expense_name_input(message: types.Message, state: FSMContext):
    await delete_user_message(message)
    name = message.text.strip()
    await delete_prev_bot_message(message, state)
    await state.update_data(name=name)
    await send_and_store(
        message,
        state,
        "💰 Введите стоимость расхода:",
        reply_markup=back_button_keyboard("back_to_name"),
    )
    await state.set_state(CreateExpenseFSM.waiting_for_cost)


# --- FSM handler для ввода стоимости ---
@router.message(CreateExpenseFSM.waiting_for_cost)
async def expense_price_input(message: types.Message, state: FSMContext):
    await delete_user_message(message)
    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число.")
        return
    await delete_prev_bot_message(message, state)
    await state.update_data(cost=price)
    await state.update_data(user_id=message.from_user.id)


    loading_msg = await message.answer("⏳ Загружаю список заказов...")
    recent_order_ids = await get_recent_order_ids(days=3)
    try:
        await loading_msg.delete()
    except:
        pass

    # 4. Показываем результат
    await send_and_store(
        message,
        state,
        "🔗 Выберите ID заказа (или нажмите Пропустить / Нет заказов):",
        reply_markup=expense_order_ids_keyboard(recent_order_ids)
    )

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
    user_id = data.get("user_id")
    if callback_data.value == "yes":
        # Пользователь подтвердил расход, записываем в Google Sheet
        await append_expense_to_sheet(data)
        await call.message.edit_text(
            "✅ Расход успешно записан!",
        )
        if user_has_role(user_id, ['admin']):
            await call.message.answer(f'Вы в панеле администратора.',
                                      reply_markup=admin_main_keyboard())
        elif user_has_role(user_id, ['manager']):
            await call.message.answer(f'Вы в панеле менеджера.',
                                      reply_markup=manager_main_keyboard())
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
