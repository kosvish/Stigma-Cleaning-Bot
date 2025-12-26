from aiogram.fsm.state import StatesGroup, State


class CreateAccessKeyFSM(StatesGroup):
    waiting_for_password = State()
    waiting_for_role = State()
