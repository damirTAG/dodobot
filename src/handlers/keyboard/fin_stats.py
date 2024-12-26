from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.services.dodo_api import DodoAPI

from src.utils import get_currency
from src.utils.formatting import format_stats
from src.utils.paginate import paginate_keyboard

import asyncio

router = Router()
dodo_api = DodoAPI()

@router.callback_query(F.data.startswith("stats_"))
async def show_stats(callback: CallbackQuery):
    country_id, pizzeria_id = callback.data.split("_")[1:]

    countries = await dodo_api.get_countries()
    country = next((c for c in countries if c.id == int(country_id)), None)
    
    if not country:
        await callback.answer("Country not found!")
        return

    pizzeria_details, stats = await asyncio.gather(
        dodo_api.get_pizzeria_details(int(pizzeria_id), country.code),
        dodo_api.get_pizzeria_stats(country_id, int(pizzeria_id))
    )
    today_stats, yesterday_stats, month_revenue = stats

    currency = get_currency(country_id, countries)

    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Назад к пиццерии", 
        callback_data=f"pizzeria_{country_id}_{pizzeria_id}"
    )
    builder.button(
        text="📍 К списку пиццерий",
        callback_data=f"city_{country_id}_{pizzeria_details.address_details.locality_id}"
    )
    builder.button(
        text="🌍 К выбору страны",
        callback_data="back_to_countries"
    )
    builder.adjust(1)


    message_text = (
        f"📊 <b>Доход пиццерии {pizzeria_details.name}:</b>\n\n"
        "<b> - на сегодня:</b>\n"
        f"{format_stats(today_stats, currency)}\n\n"
        "<b> - вчера:</b>\n"
        f"{format_stats(yesterday_stats, currency)}\n\n"
        f"<b> - за прошлый месяц:</b>\n"
        f"💰 Выручка: {month_revenue:,.2f} {currency}"
    )

    await callback.message.edit_text(
        message_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "back_to_countries")
async def back_to_countries(callback: CallbackQuery):
    countries = await dodo_api.get_countries()
    keyboard = paginate_keyboard(countries, 0, "country")
    await callback.message.edit_text(
        "Выберите страну:",
        reply_markup=keyboard
    )