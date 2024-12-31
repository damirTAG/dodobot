from aiogram import Dispatcher

from .command import (
    favorite,
    search, 
    revenue,
    stop_report
)
from .keyboard import (
    country, 
    city, 
    fin_stats, 
    pizzeria,
    users_pizzeria
)
from .inline import inline_search
from .admin import core, users

def register_handlers(dp: Dispatcher):
    dp.include_router(country.router)
    dp.include_router(city.router)
    dp.include_router(pizzeria.router)
    dp.include_router(users_pizzeria.router)
    dp.include_router(fin_stats.router)

    dp.include_router(search.router)
    dp.include_router(revenue.router)
    dp.include_router(favorite.router)
    dp.include_router(stop_report.router)

    dp.include_router(inline_search.router)
    
    dp.include_router(core.router)
    dp.include_router(users.router)