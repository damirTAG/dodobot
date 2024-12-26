from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.services.dodo_api import DodoAPI
from src.utils import paginate, formatting

router = Router()
dodo_api = DodoAPI()

# @router.callback_query(F.data.startswith("country_"))
# async def show_pizzerias(callback: CallbackQuery):
#     country_id = int(callback.data.split("_")[1])
#     pizzerias = await dodo_api.get_pizzerias(country_id)

#     country = next(c for c in await dodo_api.get_countries() if c.id == int(country_id))
#     country_stats = await dodo_api.get_country_stats(country.code)
#     country_stats_message = formatting.format_country_stats(country.name, country_stats)

#     keyboard = paginate.paginate_keyboard(pizzerias, 0, f"pizzeria_{country_id}")
    
#     await callback.message.edit_text(
#         f"{country_stats_message}\nВыберите пиццерию:",
#         reply_markup=keyboard,
#         parse_mode='html'
#     )

@router.callback_query(F.data.startswith("page_pizzeria_"))
async def process_pizzeria_page(callback: CallbackQuery):
    _, _, country_id, page = callback.data.split("_")
    pizzerias = await dodo_api.get_pizzerias(int(country_id))
    keyboard = paginate.paginate_keyboard(pizzerias, int(page), f"pizzeria_{country_id}")
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(F.data.startswith("pizzeria_"))
async def show_pizzeria_details(callback: CallbackQuery):
    country_id, pizzeria_id = callback.data.split("_")[1:]
    country = next(c for c in await dodo_api.get_countries() if c.id == int(country_id))
    pizzeria = await dodo_api.get_pizzeria_details(int(pizzeria_id), country.code)
    
    builder = InlineKeyboardBuilder()

    builder.button(
        text="📊 Показать доход",
        callback_data=f"stats_{country_id}_{pizzeria_id}"
    )
    
    builder.button(
        text="⬅️ К списку пиццерий",
        callback_data=f"city_{country_id}_{pizzeria.address_details.locality_id}"
    )
    
    builder.button(
        text="🌍 К выбору страны",
        callback_data="back_to_countries"
    )

    builder.adjust(1)
    
    await callback.message.edit_text(
        formatting.format_pizzeria_info(pizzeria),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
