from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from app.keyboards.admin import admin_main_keyboard, admin_users_keyboard
from app.services.permissions import user_has_role
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


@router.callback_query(AdminCallback.filter())
async def admin_callbacks(call: CallbackQuery, callback_data: AdminCallback):
    action = callback_data.action

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


    elif action == "categories":
        await call.answer("Категории в разработке", show_alert=True)

    elif action == "access":
        await call.answer("Доступы и пароли в разработке", show_alert=True)

    await call.answer()
