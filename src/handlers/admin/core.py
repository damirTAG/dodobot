from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src.database.actions.stats import UserStatistics
from src.database.base import db_manager
from src.misc.decorators.is_admin import admin_only
from src.utils.formatting import format_admin_statistics_response

router = Router()


@router.message(Command("admin_stats"))
@admin_only()
async def admin_stats(message: Message):
    async for session in db_manager.get_session():
        us = UserStatistics(session)
        stats = await us.get_complete_statistics()
        msg = format_admin_statistics_response(stats)
        await message.answer(msg, parse_mode='Markdown')