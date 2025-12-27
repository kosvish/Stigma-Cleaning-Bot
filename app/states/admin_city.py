from aiogram.fsm.state import StatesGroup, State


class CreateCityFSM(StatesGroup):
    waiting_for_city_name = State()