from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.auth_service import authenticate_user, user_exists
from aiogram.filters import Command

router = Router()

class AuthFSM(StatesGroup):
    waiting_for_password = State()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    if user_exists(message.from_user.id):
        await message.answer(f'С возращением {message.from_user.first_name}')
    else:
        await message.answer("🔐 Введите пароль доступа")
        await state.set_state(AuthFSM.waiting_for_password)

@router.message(AuthFSM.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    user = authenticate_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        password=message.text
    )

    if not user:
        await message.answer("❌ Неверный пароль")
        return

    await message.answer("✅ Доступ разрешён")

    await state.clear()

