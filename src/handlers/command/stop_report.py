from aiogram import Router, types
from aiogram.filters import Command

from src.database.actions import reports
from src.database.base import db_manager

router = Router()


@router.message(Command("stop"))
async def stop_report(message: types.Message):
    async for session in db_manager.get_session():
        result = await reports.remove_subscription(session, message.from_user.id)
        if result == True:
            await message.answer(
                'Хорошо, я отключил уведомления 👍'
                )
        elif result == False:
            await message.answer(
                'Ты еще не отслеживаешь пиццерию, поэтому рассылок нет.'
                '\n\nЧтобы начать отслеживать, выбери свою любимую пиццерию командой /start'
            )