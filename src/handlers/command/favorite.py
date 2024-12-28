from aiogram import Router, types
from aiogram.filters import Command
from datetime import datetime
from src.services.dodo_api import DodoAPI

from src.database.actions.user import get_user
from src.database.base import db_manager

router = Router()
dodo_api = DodoAPI()

@router.message(Command("favorite"))
async def user_favorite_handler(m: types.Message):
    user_id = m.from_user.id
    async for session in db_manager.get_session():
        user = await get_user(session, user_id)
        if not user:
            await m.answer("Пользователь не найден.")
            return

        if not user.pizzeria_id:
            await m.answer("Пиццерия не указана.")
            return

        pizzeria_data = await dodo_api.get_pizzeria_details_global(user.country_id, user.pizzeria_id)
        if not pizzeria_data:
            await m.answer("Информация о пиццерии не найдена.")
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
        days_following = (datetime.now() - active_since_date).days

        message = (
            f'Отслеживаемая пиццерия {pizzeria_info["countryName"]}, {pizzeria_info["pizzeria"]["alias"]}, '
            f'по адресу {pizzeria_info["pizzeria"]["address"]["text"]}'
            f"\n\nЗа этой точкой ты следишь с {formatted_date} ({days_following} дней) "
            f"\n\nЧтобы перестать отслеживать - /stop"
        )
        await m.answer(message)