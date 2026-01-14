from aiogram.fsm.state import StatesGroup, State

class CreateExpenseFSM(StatesGroup):
    waiting_for_type = State()
    waiting_for_category = State()
    waiting_for_subcategory = State()
    waiting_for_brand = State()
    waiting_for_quantity = State()
    waiting_for_name = State()
    waiting_for_cost = State()
    waiting_for_order_id = State()
    waiting_for_city = State()
    waiting_for_confirm = State()
    waiting_for_receipt = State()
