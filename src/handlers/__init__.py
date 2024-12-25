from aiogram import Dispatcher
from . import country, fin_stats, pizzeria, search
from .inline import inline_search

def register_handlers(dp: Dispatcher):
    dp.include_router(country.router)
    dp.include_router(pizzeria.router)
    dp.include_router(fin_stats.router)
    dp.include_router(search.router)
    dp.include_router(inline_search.router)