from aiogram import BaseMiddleware
from app.database.session import SessionLocal
from app.database.models.user import User


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        with SessionLocal() as session:
            user = session.query(User).filter(
                User.telegram_id == event.from_user.id
            ).first()

            if not user or not user.is_active:
                await event.answer("🚫 Доступ запрещён")
                return None

        return await handler(event, data)
