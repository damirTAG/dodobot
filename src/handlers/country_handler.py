from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from src.services.dodo_api import DodoAPI
from src.utils.paginate import paginate_keyboard

router = Router()
dodo_api = DodoAPI()

@router.message(Command("start"))
async def start_command(message: Message):
    countries = await dodo_api.get_countries()
    keyboard = paginate_keyboard(countries, 0, "country")
    await message.answer(f"Приветствую!\nЯ бот который покажет вам информацию о вашей любимой точке додо пицце."
                         f"\n\nИспользуйте команду /search\nПример: /search ru томск\n"
                         f"Также доступен инлайн-мод: <code>@DodoIS_simplebot kz алматы</code>"
                         f"\n\nЛибо выберите страну:", 
                         reply_markup=keyboard,
                         parse_mode='html'
                         )

@router.callback_query(F.data.startswith("page_country_"))
async def process_country_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    countries = await dodo_api.get_countries()
    keyboard = paginate_keyboard(countries, page, "country")
    await callback.message.edit_reply_markup(reply_markup=keyboard)