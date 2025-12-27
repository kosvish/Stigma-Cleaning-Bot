from aiogram import Router, F

from app.keyboards.admin_brands import brands_list_keyboard
from app.keyboards.manager import manager_main_keyboard
from app.services.permissions import user_has_role
from aiogram import Router, types, F

from app.utils.roles import UserRole

router = Router()
