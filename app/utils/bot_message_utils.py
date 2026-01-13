from aiogram.types import Message
from aiogram.fsm.context import FSMContext


async def delete_prev_bot_message(message: Message, state: FSMContext):
    data = await state.get_data()
    prev_msg_id = data.get("last_bot_message_id")

    if prev_msg_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=prev_msg_id
            )
        except Exception:
            pass  # сообщение могло быть уже удалено


async def send_and_store(message: Message, state: FSMContext, text: str, **kwargs):
    sent = await message.answer(text, **kwargs)
    await state.update_data(last_bot_message_id=sent.message_id)


async def delete_user_message(message: Message):
    """Безопасное удаление сообщения пользователя"""
    try:
        await message.delete()
    except Exception:
        pass
