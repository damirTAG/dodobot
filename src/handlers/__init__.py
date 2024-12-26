from aiogram import Dispatcher

from .command import search, revenue
from .keyboard import country, city, fin_stats, pizzeria
from .inline import inline_search

def register_handlers(dp: Dispatcher):
    dp.include_router(country.router)
    dp.include_router(city.router)
    dp.include_router(pizzeria.router)
    dp.include_router(fin_stats.router)

    dp.include_router(search.router)
    dp.include_router(revenue.router)

    dp.include_router(inline_search.router)