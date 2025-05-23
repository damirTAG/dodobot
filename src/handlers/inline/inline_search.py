from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from src.services.dodo_api import DodoAPI
from src.utils.formatting import format_pizzeria_info, format_revenue

router = Router()
dodo_api = DodoAPI()


@router.inline_query()
async def handle_pizzeria_inline_search(query: types.InlineQuery):
    search_query = query.query.strip()

    if not search_query:
        total_revenue = await dodo_api.get_total_revenue_last_month()
        total_rev_formatted = format_revenue(total_revenue)
        results = [
            InlineQueryResultArticle(
                id="total_revenue",
                title="Доход всех пиццерий за этот месяц",
                input_message_content=InputTextMessageContent(
                    message_text=f"<b>Доход всех пиццерий Dodo за этот месяц</b>: \n\n{total_rev_formatted}",
                    parse_mode="html"
                )
            )
        ]
        return await query.answer(results, cache_time=60)

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
                title=f'{pizzeria.alias} ({pizzeria.name})',
                description=pizzeria.address,
                thumbnail_url='https://www.oxfordeagle.com/wp-content/uploads/sites/38/2020/07/Dodo-Pizza-Logo.jpg?w=960',
                # еще думаю по поводу тамбнейла
                input_message_content=InputTextMessageContent(
                    message_text=f"{format_pizzeria_info(pizzeria)}",
                    parse_mode='html'
                ),
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
