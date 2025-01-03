from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from src.services.dodo_api import DodoAPI
from src.utils.paginate import paginate_keyboard

router = Router()
dodo_api = DodoAPI()

@router.message(Command("search"))
async def handle_pizzeria_search(message: types.Message):
    parts = message.text.strip().split(maxsplit=2)

    if len(parts) < 3:
        await message.answer("Пожалуйста, используйте формат команды: /search {country_code} {name}\nПример: /search ru томск")
        return

    country_code, search_query = parts[1], parts[2]

    pizzerias = await dodo_api.search_pizzerias_by_name(country_code, search_query)

    if pizzerias:
        country_id = pizzerias[0].country_id
        keyboard = []
        
        for pizzeria in pizzerias:
            keyboard_text = f'{pizzeria.name} ({pizzeria.address})' 
            keyboard.append([
                InlineKeyboardButton(
                    text=keyboard_text,
                    callback_data=f"pizzeria_{country_id}_{pizzeria.id}"
                )
            ])

        await message.answer(
            f"Нашли пиццерии, которые соответствуют запросу '{search_query}':",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        await message.answer(f"Извините, пиццерий по запросу '{search_query}' в стране {country_code} не найдено.")
