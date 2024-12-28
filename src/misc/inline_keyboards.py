from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from src.services.dodo_api import Country, Pizzeria

def get_countries_keyboard(countries: List[Country]) -> InlineKeyboardMarkup:
    keyboard = []
    for country in countries:
        keyboard.append([
            InlineKeyboardButton(
                text=country.name,
                callback_data=f"country_{country.id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_pizzerias_keyboard(pizzerias: List[Pizzeria]) -> InlineKeyboardMarkup:
    keyboard = []
    for pizzeria in pizzerias:
        keyboard.append([
            InlineKeyboardButton(
                text=pizzeria.name,
                callback_data=f"pizzeria_{pizzeria.uuid}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)