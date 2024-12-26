from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.services.dodo_api import DodoAPI
from src.utils import paginate, formatting

router = Router()
dodo_api = DodoAPI()

@router.callback_query(F.data.startswith("country_"))
async def show_cities(callback: CallbackQuery):
    country_id = int(callback.data.split("_")[1])
    country = next(c for c in await dodo_api.get_countries() if c.id == int(country_id))

    cities = await dodo_api.get_cities(country.code)

    country_stats = await dodo_api.get_country_stats(country.code)
    country_stats_message = formatting.format_country_stats(country.name, country_stats)
    
    keyboard = paginate.paginate_keyboard(cities, 0, f"city_{country_id}")
    
    await callback.message.edit_text(
        f"{country_stats_message}\nВыберите город:",
        reply_markup=keyboard,
        parse_mode='html'
    )

@router.callback_query(F.data.startswith("page_city_"))
async def process_city_page(callback: CallbackQuery):
    _, _, country_id, page = callback.data.split("_")
    country = next(c for c in await dodo_api.get_countries() if c.id == int(country_id))
    cities = await dodo_api.get_cities(country.code)
    keyboard = paginate.paginate_keyboard(cities, int(page), f"city_{country_id}")
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(F.data.startswith("city_"))
async def show_city_pizzerias(callback: CallbackQuery):
    country_id, city_id = callback.data.split("_")[1:]
    country = next(c for c in await dodo_api.get_countries() if c.id == int(country_id))
    
    cities = await dodo_api.get_cities(country.code)
    selected_city = next(city for city in cities if str(city.id) == city_id)
    
    city_pizzerias = await dodo_api.get_pizzerias_by_name(country.code, selected_city.name)
    
    keyboard = paginate.paginate_keyboard(
        city_pizzerias, 
        0, 
        f"pizzeria_{country_id}",
        country_id=int(country_id),
        city_id=int(city_id)
    )
    
    await callback.message.edit_text(
        f"Пиццерии в городе {selected_city.name}:",
        reply_markup=keyboard,
        parse_mode='html'
    )