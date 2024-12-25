from aiogram import Dispatcher
from . import country_handler, pizzeria_handler, stats_handler, search_handler
from .inline import search

def register_handlers(dp: Dispatcher):
    dp.include_router(country_handler.router)
    dp.include_router(pizzeria_handler.router)
    dp.include_router(stats_handler.router)
    dp.include_router(search_handler.router)
    dp.include_router(search.router)