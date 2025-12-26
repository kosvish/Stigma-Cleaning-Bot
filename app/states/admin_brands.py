from aiogram.fsm.state import StatesGroup, State


class AdminBrandFSM(StatesGroup):
    waiting_for_brand_name = State()
