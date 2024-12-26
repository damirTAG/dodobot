from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from src.models.basic import Pizzeria, PizzeriaLite

ITEMS_PER_PAGE = 8

def paginate_keyboard(items, page: int, prefix: str, country_id: int = None, city_id: int = None):
    builder = InlineKeyboardBuilder()
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    for item in items[start:end]:
        text = item.name
        if isinstance(item, Pizzeria) and item.address:
            text = f"{item.address}"
        elif isinstance(item, PizzeriaLite) and item.address:
            text = f"{item.address.text}"
        builder.button(
            text=text,
            callback_data=f"{prefix}_{item.id}"
        )

    builder.adjust(2)

    if len(items) > ITEMS_PER_PAGE:
        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=f"page_{prefix}_{page-1}"
                )
            )
        if end < len(items):
            navigation_buttons.append(
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"page_{prefix}_{page+1}"
                )
            )
        builder.row(*navigation_buttons, width=2)

    if prefix != 'country':
        if prefix == 'pizzeria' and city_id is not None:
            builder.button(
                text="К выбору пиццерии",
                callback_data=f"city_{country_id}_{city_id}"
            )

        builder.button(
            text="Назад к странам",
            callback_data="back_to_countries"
        )

    return builder.as_markup()