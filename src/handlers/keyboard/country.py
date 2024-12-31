from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from src.services.dodo_api import DodoAPI
from src.utils.paginate import paginate_keyboard
from src.misc.decorators.is_new_user import is_new_user
from src.misc.ui.show import start_text

router = Router()
dodo_api = DodoAPI()

@router.message(Command("start"))
@is_new_user()
async def start_command(message: Message):
    countries = await dodo_api.get_countries()
    keyboard = paginate_keyboard(countries, 0, "country")
    await message.answer(text=start_text, 
                         reply_markup=keyboard,
                         parse_mode='html'
                         )

@router.callback_query(F.data.startswith("page_country_"))
async def process_country_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    countries = await dodo_api.get_countries()
    keyboard = paginate_keyboard(countries, page, "country")
    await callback.message.edit_reply_markup(reply_markup=keyboard)