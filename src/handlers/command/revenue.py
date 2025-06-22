from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from src.services.dodo_api import DodoAPI
from src.utils.graph import generate_revenue_chart

router = Router()
dodo_api = DodoAPI()

@router.message(Command("revenue"))
async def total_last_month_revenue(message: types.Message):
    total_revenue = await dodo_api.get_total_revenue_last_month()

    if not total_revenue:
        await message.answer("❌ Данных о доходах за прошлый месяц нет.")
        return

    chart_image = await generate_revenue_chart(total_revenue)
    chart_bytes = chart_image.getvalue()
    chart_file = BufferedInputFile(chart_bytes, filename="revenue_chart.png")

    await message.answer_photo(
        photo=chart_file,
        caption="<b>Доход всех пиццерий Dodo за этот месяц</b>",
        parse_mode="html"
    )