from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from src.models.basic import Pizzeria, PizzeriaLite
from src.database.models.User import User

ITEMS_PER_PAGE = 8

def paginate_keyboard(items, page: int, prefix: str, country_id: int = None, city_id: int = None):
    builder = InlineKeyboardBuilder()
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    for item in items[start:end]:
        if isinstance(item, Pizzeria) and item.address:
            text = f"{item.address}"
            callback_data=f"{prefix}_{item.id}"
        elif isinstance(item, PizzeriaLite) and item.address:
            text = f"{item.address.text}"
            callback_data=f"{prefix}_{item.id}"
        elif isinstance(item, User) and item.telegram_id:
            text = f"{item.telegram_id}"
            callback_data=f"{prefix}_{item.telegram_id}"
        else:
            text = item.name
            callback_data=f"{prefix}_{item.id}"
        builder.button(
            text=text,
            callback_data=callback_data
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

    if prefix not in  ['country', 'user', 'users']:
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