from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime
from pytz import timezone
from src.services.dodo_api import DodoAPI

from src.database.actions.user import get_user
from src.database.base import db_manager

router = Router()
dodo_api = DodoAPI()

@router.callback_query(F.data.startswith("userfollowingpizzeria"))
async def user_following_pizzeria(callback: CallbackQuery):
    user_id = callback.from_user.id
    async for session in db_manager.get_session():
        user = await get_user(session, user_id)
        if not user:
            await callback.message.answer("Пользователь не найден.")
            return

        if not user.pizzeria_id:
            await callback.message.answer("Пиццерия не указана.")
            return

        pizzeria_data = await dodo_api.get_pizzeria_details_global(user.country_id, user.pizzeria_id)
        if not pizzeria_data:
            await callback.message.answer("Информация о пиццерии не найдена.")
            return
        
        if isinstance(pizzeria_data, list) and len(pizzeria_data) > 0:
            pizzeria_info = pizzeria_data[0]
        else:
            pizzeria_info = pizzeria_data 
        if isinstance(user.active_since, datetime):
            active_since_date = user.active_since
        else:
            active_since_date = datetime.combine(user.active_since, datetime.min.time())

        formatted_date = active_since_date.strftime("%Yг. %d %b")
        
        tz = timezone('Asia/Oral')
        active_since_date = tz.localize(active_since_date)
        days_following = (datetime.now(timezone('Asia/Oral')) - active_since_date).days

        message = (
            f'Отслеживаемая пиццерия {pizzeria_info["countryName"]}, {pizzeria_info["pizzeria"]["alias"]}, '
            f'по адресу {pizzeria_info["pizzeria"]["address"]["text"]}'
            f"\n\nЗа этой точкой ты следишь с {formatted_date} ({days_following} дней) "
            f"\n\nЧтобы перестать отслеживать - /stop"
        )
        await callback.message.answer(message)