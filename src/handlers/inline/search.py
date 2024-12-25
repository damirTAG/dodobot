from aiogram import Router, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from src.services.dodo_api import DodoAPI
from src.utils.formatting import format_pizzeria_info

router = Router()
dodo_api = DodoAPI()


@router.inline_query()
async def handle_pizzeria_inline_search(query: types.InlineQuery):
    search_query = query.query.strip()

    if not search_query:
        results = []
        await query.answer(results)
        return

    parts = search_query.split(maxsplit=1)

    if len(parts) < 2:
        results = [
            InlineQueryResultArticle(
                id="0",
                title="Неверный формат поиска",
                input_message_content=InputTextMessageContent(
                    message_text="Пожалуйста, используйте формат: {country_code} {name}\nПример: ru томск"
                )
            )
        ]
        await query.answer(results)
        return

    country_code, name_query = parts[0], parts[1]
    # print(country_code, name_query)

    pizzerias = await dodo_api.search_pizzerias_by_name(country_code, name_query)

    if pizzerias:
        results = [
            InlineQueryResultArticle(
                id=str(i),
                title=pizzeria.name,
                input_message_content=InputTextMessageContent(
                    message_text=f"{format_pizzeria_info(pizzeria)}",
                    parse_mode='html'
                )
            )
            for i, pizzeria in enumerate(pizzerias)
            
        ]
        await query.answer(results, cache_time=60)
    else:
        results = [
            InlineQueryResultArticle(
                id="0",
                title="Нет пиццерий",
                input_message_content=InputTextMessageContent(message_text="Извините, пиццерий по запросу не найдено.")
            )
        ]
        await query.answer(results, cache_time=60)
