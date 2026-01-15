from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.keyboards.admin import admin_main_keyboard
from app.keyboards.manager import manager_main_keyboard
from app.services.access_keys_service import get_key_by_password
from app.services.auth_service import authenticate_user, user_exists, check_global_password
from aiogram.filters import Command

from app.services.permissions import user_has_role

router = Router()


class AuthFSM(StatesGroup):
    waiting_for_password = State()
    waiting_for_platrum_id = State()


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    print("start")
    # Если пользователь уже есть в базе
    if user_exists(message.from_user.id):
        if user_has_role(message.from_user.id, ['admin']):
            await message.answer(
                f'С возвращением, Админ {message.from_user.first_name}',
                reply_markup=admin_main_keyboard()
            )
        elif user_has_role(message.from_user.id, ['manager']):
            await message.answer(
                f'С возвращением, Менеджер',
                reply_markup=manager_main_keyboard()
            )
        else:
            # Для других ролей (или если роль не определена)
            await message.answer("С возвращением!")
    else:
        # Если пользователя нет - начинаем регистрацию
        await message.answer("🔐 Введите пароль доступа:")
        await state.set_state(AuthFSM.waiting_for_password)


# --- ЭТАП 1: ПРОВЕРКА ПАРОЛЯ ---
@router.message(AuthFSM.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    # Удаляем сообщение с паролем для безопасности (если бот админ)
    try:
        await message.delete()
    except:
        pass

    password = message.text.strip()
    access_key = get_key_by_password(password)


    if not access_key:
        msg = await message.answer("❌ Неверный пароль. Попробуйте снова:")
        return

    await state.update_data(password=message.text.strip())

    await message.answer(
        "✅ Пароль принят!\n\n"
        "🆔 <b>Введите ваш ID сотрудника в Platrum:</b>\n"
        "<i>(Числовой ID, например: 345)</i>",
        parse_mode="HTML"
    )

    # Переходим к следующему шагу
    await state.set_state(AuthFSM.waiting_for_platrum_id)


# --- ЭТАП 2: ВВОД PLATRUM ID И СОЗДАНИЕ ЮЗЕРА ---
@router.message(AuthFSM.waiting_for_platrum_id)
async def process_platrum_id(message: types.Message, state: FSMContext):
    platrum_id = message.text.strip()



    # Достаем сохраненную роль из шага с паролем
    data = await state.get_data()
    password = data.get("password", "user")

    # Создаем пользователя в БД (Функция из прошлого ответа)
    user = authenticate_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,  # Добавил full_name, если он нужен в create_user
        platrum_id=platrum_id,  # <--- Записываем ID,
        password=password
    )

    if user:
        await message.answer(f"✅ Регистрация завершена!")
        await state.clear()

        # Сразу перенаправляем на логику старта (чтобы открылось меню)
        await start(message, state)
    else:
        await message.answer("❌ Ошибка при создании пользователя. Обратитесь к администратору.")
        await state.clear()
