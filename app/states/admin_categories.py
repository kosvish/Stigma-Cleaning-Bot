from aiogram.fsm.state import StatesGroup, State


class AdminCategoryFSM(StatesGroup):
    waiting_for_category_name = State()
