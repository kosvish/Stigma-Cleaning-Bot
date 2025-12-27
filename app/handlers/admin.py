from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from app.keyboards.admin import admin_main_keyboard, admin_users_keyboard, city_admin_keyboard, cities_list_keyboard
from app.services.cities_service import add_city, get_all_cities, delete_city

from app.services.permissions import user_has_role
from app.states.admin_city import CreateCityFSM
from app.utils.roles import UserRole
from app.utils.callbacks import AdminCallback
from app.services.users_service import (
    get_all_users,
    get_user_by_id,
    delete_user, update_user_city, update_user_role
)
from app.keyboards.admin_users import (
    users_list_keyboard,
    user_actions_keyboard,
    user_edit_keyboard,
    user_city_keyboard,
    user_role_keyboard
)

from app.services.access_keys_service import (
    get_all_keys,
    create_access_key,
    delete_key
)
from app.keyboards.admin_access import (
    admin_access_keyboard,
    access_keys_list_keyboard,
    access_key_actions_keyboard,
    access_roles_keyboard
)
from aiogram.fsm.context import FSMContext
from app.states.admin_access import CreateAccessKeyFSM
from app.services.expense_categories_service import (
    get_all_categories,
    create_category,
    delete_category, get_category_by_id
)
from app.keyboards.admin_categories import (
    categories_main_keyboard,
    categories_list_keyboard
)
from app.states.admin_categories import AdminCategoryFSM
from app.services.expense_subcategories_service import (
    get_subcategories_by_category,
    create_subcategory,
    delete_subcategory
)
from app.keyboards.admin_subcategories import subcategories_list_keyboard
from app.states.admin_subcategories import AdminSubCategoryFSM
from app.services.expense_brands_service import (
    get_brands_by_category,
    create_brand,
    delete_brand
)
from app.keyboards.admin_brands import brands_list_keyboard
from app.states.admin_brands import AdminBrandFSM

router = Router()


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not user_has_role(message.from_user.id, [UserRole.ADMIN]):
        await message.answer("⛔ У вас нет доступа")
        return

    await message.answer(
        "🛠 <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(AdminCallback.filter(F.role == 'admin'))
async def admin_callbacks(call: CallbackQuery, callback_data: AdminCallback, state: FSMContext):
    action = callback_data.action
    current_state = await state.get_state()
    # Если мы в FSM создания пароля
    if current_state == CreateAccessKeyFSM.waiting_for_role.state:
        role = callback_data.value
        data = await state.get_data()
        password = data.get("password")

        create_access_key(password=password, role=role)
        await state.clear()

        await call.message.edit_text(
            f"✅ <b>Пароль создан</b>\n\n"
            f"Пароль: <code>{password}</code>\n"
            f"Роль: {role}",
            reply_markup=admin_access_keyboard(),
            parse_mode="HTML"
        )
        await call.answer()
        return  # важно! чтобы дальше код admin_callbacks не выполнялся
    # Управление пользователями
    if action == "users":
        await call.message.edit_text(
            "👤 <b>Управление пользователями</b>\n\n"
            "Выберите действие:",
            reply_markup=admin_users_keyboard(),
            parse_mode="HTML"
        )

    # Назад в главное меню
    elif action == "back":
        await call.message.edit_text(
            "🛠 <b>Админ-панель</b>\n\n"
            "Выберите действие:",
            reply_markup=admin_main_keyboard(),
            parse_mode="HTML"
        )

    # Заглушки (пока)
    elif action == "users_list":
        users = get_all_users()

        if not users:
            await call.message.edit_text(
                "👤 Пользователи не найдены",
                reply_markup=admin_users_keyboard(),
                parse_mode="HTML"
            )
            return

        await call.message.edit_text(
            "👤 <b>Активные пользователи</b>\n\n"
            "Выберите пользователя:",
            reply_markup=users_list_keyboard(users),
            parse_mode="HTML"
        )
    elif action == "user_view":
        user = get_user_by_id(callback_data.user_id)

        if not user:
            await call.answer("Пользователь не найден", show_alert=True)
            return

        await call.message.edit_text(
            f"👤 <b>Пользователь</b>\n\n"
            f"Имя: {user.full_name}\n"
            f"Username: @{user.username}\n"
            f"Роль: {user.role}\n"
            f"Город: {user.city}\n"
            f"ID: {user.telegram_id}",
            reply_markup=user_actions_keyboard(user.telegram_id),
            parse_mode="HTML"
        )


    elif action == "user_delete":
        success = delete_user(callback_data.user_id)
        if success:
            await call.answer("Пользователь удалён")
        else:
            await call.answer("Ошибка удаления", show_alert=True)

        users = get_all_users()
        await call.message.edit_text(
            "👤 <b>Активные пользователи</b>",
            reply_markup=users_list_keyboard(users),
            parse_mode="HTML"
        )

    elif action == "user_edit":
        user = get_user_by_id(callback_data.user_id)

        await call.message.edit_text(
            f"✏️ <b>Редактирование пользователя</b>\n\n"
            f"Имя: {user.full_name}\n"
            f"Роль: {user.role}\n"
            f"Город: {user.city}",
            reply_markup=user_edit_keyboard(user.telegram_id),
            parse_mode="HTML"
        )

    elif action == "user_change_city":
        await call.message.edit_text(
            "🏙 <b>Выберите город</b>",
            reply_markup=user_city_keyboard(callback_data.user_id),
            parse_mode="HTML"
        )

    elif action == "user_set_city":
        update_user_city(callback_data.user_id, callback_data.value)
        await call.answer("Город обновлён")

        # Возвращаемся в редактирование
        await call.message.edit_text(
            "✅ Город успешно изменён",
            reply_markup=user_edit_keyboard(callback_data.user_id)
        )

    elif action == "user_change_role":
        await call.message.edit_text(
            "🧩 <b>Выберите роль</b>",
            reply_markup=user_role_keyboard(callback_data.user_id),
            parse_mode="HTML"
        )


    elif action == "user_set_role":
        update_user_role(callback_data.user_id, callback_data.value)
        await call.answer("Роль обновлена")
        await call.message.edit_text(
            "✅ Роль успешно изменена",
            reply_markup=user_edit_keyboard(callback_data.user_id)
        )



    elif action == "access":

        await call.message.edit_text(

            "🔐 <b>Доступы и пароли</b>",

            reply_markup=admin_access_keyboard(),

            parse_mode="HTML"

        )
    elif action == "access_list":
        keys = get_all_keys()

        await call.message.edit_text(
            "📋 <b>Пароли доступа</b>",
            reply_markup=access_keys_list_keyboard(keys),
            parse_mode="HTML"
        )
    elif action == "access_view":
        key_id = int(callback_data.value)

        keys = get_all_keys()
        key = next((k for k in keys if k.id == key_id), None)

        if not key:
            await call.answer("Ключ не найден", show_alert=True)
            return

        await call.message.edit_text(
            f"🔐 <b>Пароль</b>\n\n"
            f"Значение: <code>{key.password}</code>\n"
            f"Роль: {key.role}\n"
            f"Использован: {key.used_count} раз\n"
            f"Активен: {'Да' if key.is_active else 'Нет'}",
            reply_markup=access_key_actions_keyboard(key.id),
            parse_mode="HTML"
        )

    elif action == "access_deactivate":
        key_id = int(callback_data.value)
        delete_key(key_id)

        await call.answer("Пароль удалён")

        keys = get_all_keys()
        await call.message.edit_text(
            "📋 <b>Пароли доступа</b>",
            reply_markup=access_keys_list_keyboard(keys),
            parse_mode="HTML"
        )
    elif action == "access_create":
        await call.message.edit_text(
            "🔐 <b>Создание пароля</b>\n\n"
            "Введите пароль для доступа:",
            parse_mode="HTML"
        )
        await state.set_state(CreateAccessKeyFSM.waiting_for_password)
    elif action == "categories":
        await call.message.edit_text(
            "📂 <b>Категории</b>\n\nВыберите раздел:",
            reply_markup=categories_main_keyboard(),
            parse_mode="HTML"
        )

    # ------------КАТЕГОРИИ------------#
    # ------------КАТЕГОРИИ------------#
    # ------------КАТЕГОРИИ------------#
    elif action == "category_list":
        categories = get_all_categories()

        if not categories:
            await call.message.edit_text(
                "📦 Категории пока не созданы",
                reply_markup=categories_list_keyboard([]),
                parse_mode="HTML"
            )
            return

        await call.message.edit_text(
            "📦 <b>Категории расходов</b>\n\n"
            "Нажмите, чтобы удалить:",
            reply_markup=categories_list_keyboard(categories),
            parse_mode="HTML"
        )


    elif action == "category_create":
        await call.message.edit_text(
            "➕ <b>Создание категории</b>\n\n"
            "Введите название категории:",
            parse_mode="HTML"
        )
        await state.set_state(AdminCategoryFSM.waiting_for_category_name)

    elif action == "category_delete":
        category_id = int(callback_data.value)
        delete_category(category_id)
        await call.answer("Категория удалена")
        categories = get_all_categories()
        await call.message.edit_text(
            "📂 <b>Категории расходов</b>",
            reply_markup=categories_list_keyboard(categories),
            parse_mode="HTML"
        )

    # ------------ПОДКАТЕГОРИИ------------#
    # ------------ПОДКАТЕГОРИИ------------#
    # ------------ПОДКАТЕГОРИИ------------#

    elif action == "subcategory_list":
        category_id = int(callback_data.value)
        category = get_category_by_id(category_id)
        if category:
            subcategories = get_subcategories_by_category(category_id)
            await call.message.edit_text(
                f"📂 <b>{category.name}</b>\n\n"
                "Подкатегории:",
                reply_markup=subcategories_list_keyboard(
                    category_id,
                    category.name,
                    subcategories
                ),
                parse_mode="HTML"
            )
        else:
            await call.answer('Данной категории не существует')

    elif action == "subcategory_create":
        category_id = int(callback_data.value)

        await state.update_data(category_id=category_id)
        await call.message.edit_text(
            "➕ <b>Создание подкатегории</b>\n\n"
            "Введите название:",
            parse_mode="HTML"
        )
        await state.set_state(AdminSubCategoryFSM.waiting_for_subcategory_name)


    elif action == "subcategory_delete":
        sub_id = int(callback_data.value)
        delete_subcategory(sub_id)

        await call.answer("Подкатегория удалена")

    # ------------БРЕНДЫ------------#
    elif action == "brand_list":
        category_id = int(callback_data.value)
        brands = get_brands_by_category(category_id)

        await call.message.edit_text(
            "📦 <b>Бренды</b>",
            reply_markup=brands_list_keyboard(category_id, brands),
            parse_mode="HTML"
        )

    elif action == "brand_create":
        category_id = int(callback_data.value)

        await state.update_data(category_id=category_id)
        await call.message.edit_text(
            "➕ <b>Создание бренда</b>\n\n"
            "Введите название бренда:",
            parse_mode="HTML"
        )
        await state.set_state(AdminBrandFSM.waiting_for_brand_name)

    elif action == "brand_delete":
        brand_id = int(callback_data.value)
        delete_brand(brand_id)

        await call.answer("Бренд удалён")

    elif action == 'city':
        await call.message.edit_text(
            "🏙 <b>Управление городами</b>",
            reply_markup=city_admin_keyboard(),
            parse_mode="HTML"
        )
        await call.answer()
    elif action == 'city_list':
        cities = get_all_cities()

        await call.message.edit_text(
            "📋 <b>Список городов</b>\n\n"
            "Нажмите на город, чтобы удалить:",
            reply_markup=cities_list_keyboard(cities),
            parse_mode="HTML"
        )
    elif action == 'city_delete':
        city_id = int(callback_data.value)
        delete_city(city_id)
        await call.answer("Город удалён")
    elif action == "city_add":
        await call.message.edit_text(
            "➕ <b>Создание города</b>\n\n"
            "Введите название города:",
            parse_mode="HTML"
        )
        await state.set_state(CreateCityFSM.waiting_for_city_name)
    await call.answer()


@router.message(CreateCityFSM.waiting_for_city_name)
async def add_city_name(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if not name:
        await message.answer("❌ Название не может быть пустым")
        return

    add_city(name)

    await state.clear()
    await message.answer(
        f"✅ Город <b>{name}</b> добавлен",
        reply_markup=city_admin_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()


@router.message(CreateAccessKeyFSM.waiting_for_password)
async def access_password_input(message: types.Message, state: FSMContext):
    password = message.text.strip()

    if len(password) < 4:
        await message.answer("❌ Пароль слишком короткий. Минимум 4 символа.")
        return

    await state.update_data(password=password)

    await message.answer(
        "🧩 Выберите роль для этого пароля:",
        reply_markup=access_roles_keyboard(message.from_user.id),
    )

    await state.set_state(CreateAccessKeyFSM.waiting_for_role)


@router.message(AdminCategoryFSM.waiting_for_category_name)
async def category_name_input(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 3:
        await message.answer("❌ Слишком короткое название")
        return

    success = create_category(name)

    if not success:
        await message.answer("❌ Такая категория уже существует")
        return

    await state.clear()

    categories = get_all_categories()
    await message.answer(
        "✅ Категория создана",
        reply_markup=categories_list_keyboard(categories)
    )


@router.message(AdminSubCategoryFSM.waiting_for_subcategory_name)
async def subcategory_name_input(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("❌ Слишком короткое название")
        return

    data = await state.get_data()
    category_id = data["category_id"]

    success = create_subcategory(category_id, name)

    if not success:
        await message.answer("❌ Такая подкатегория уже существует")
        return

    await state.clear()

    subs = get_subcategories_by_category(category_id)
    category = get_category_by_id(category_id)
    await message.answer(
        "✅ Подкатегория создана",
        reply_markup=subcategories_list_keyboard(category_id, category.name, subs)
    )


@router.message(AdminBrandFSM.waiting_for_brand_name)
async def brand_name_input(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("❌ Слишком короткое название")
        return

    data = await state.get_data()
    category_id = data["category_id"]

    success = create_brand(category_id, name)
    if not success:
        await message.answer("❌ Такой бренд уже существует")
        return

    await state.clear()

    brands = get_brands_by_category(category_id)
    await message.answer(
        "✅ Бренд добавлен",
        reply_markup=brands_list_keyboard(category_id, brands)
    )
