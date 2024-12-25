from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

ITEMS_PER_PAGE = 8

def paginate_keyboard(items, page: int, prefix: str):
    builder = InlineKeyboardBuilder()
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    for item in items[start:end]:
        builder.button(
            text=item.name,
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
        builder.row(*navigation_buttons)
    return builder.as_markup()