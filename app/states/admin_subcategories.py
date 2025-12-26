from aiogram.fsm.state import StatesGroup, State


class AdminSubCategoryFSM(StatesGroup):
    waiting_for_subcategory_name = State()
