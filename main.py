from aiogram import Bot, Dispatcher
from app.config import BOT_TOKEN
from app.handlers.start import router as start_router
from app.handlers.admin import router as admin_router
from app.handlers.create_expenses import router as expense_router
from app.handlers.cleaning_price import router as price_router
from app.database.base import Base
from app.database.session import engine
from aiogram.fsm.storage.memory import MemoryStorage


def on_startup():
    Base.metadata.create_all(bind=engine)


def main():
    on_startup()

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()  # ← обязательная строчка!
    dp = Dispatcher(storage=storage)
    dp.include_router(start_router)
    dp.include_router(expense_router)
    dp.include_router(admin_router)
    dp.include_router(price_router)
    # Запуск бота
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
