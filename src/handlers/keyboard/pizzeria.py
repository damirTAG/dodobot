from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from src.services.dodo_api import DodoAPI
from src.utils import paginate, formatting
from src.database.base import db_manager
from src.database.actions.reports import add_subscription, get_user_subscriptions

router = Router()
dodo_api = DodoAPI()

@router.callback_query(F.data.startswith("page_pizzeria_"))
async def process_pizzeria_page(callback: CallbackQuery):
    _, _, country_id, city_id, page = callback.data.split("_")
    country = next(c for c in await dodo_api.get_countries() if c.id == int(country_id))
    
    cities = await dodo_api.get_cities(country.code)
    selected_city = next(city for city in cities if str(city.id) == city_id)
    
    pizzerias = await dodo_api.get_pizzerias_by_name(int(country_id))
    keyboard = paginate.paginate_keyboard(pizzerias, int(page), f"pizzeria_{country_id}")
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(F.data.startswith("pizzeria_"))
async def show_pizzeria_details(callback: CallbackQuery):
    country_id, pizzeria_id = callback.data.split("_")[1:]
    country = next(c for c in await dodo_api.get_countries() if c.id == int(country_id))
    pizzeria = await dodo_api.get_pizzeria_details(int(pizzeria_id), country.code)
    
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="📊 Показать доход",
        callback_data=f"stats_{country_id}_{pizzeria_id}"
    )
    
    builder.button(
        text="🔔 Отслеживать",
        callback_data=f"track_{country_id}_{pizzeria_id}"
    )
    
    builder.button(
        text="⬅️ К списку пиццерий",
        callback_data=f"city_{country_id}_{pizzeria.address_details.locality_id}"
    )
    
    builder.button(
        text="🌍 К выбору страны",
        callback_data="back_to_countries"
    )
    
    builder.adjust(1)
    
    await callback.message.edit_text(
        formatting.format_pizzeria_info(pizzeria),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("track_"))
async def ask_tracking_confirmation(callback: CallbackQuery):
    country_id, pizzeria_id = callback.data.split("_")[1:]
    
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Гоу",
        callback_data=f"confirm_track_{country_id}_{pizzeria_id}"
    )
    builder.button(
        text="❌ Нее",
        callback_data=f"pizzeria_{country_id}_{pizzeria_id}"
    )
    builder.adjust(2)
    
    await callback.message.edit_text(
        "Что значит отслеживать? 🤔\n\n"
        "При выборе этой пиццерии для отслеживания, "
        "вам будут приходить ежедневные сообщения в 00:00, "
        "с полными доходами за этот день.\n\n"
        "Гоу? 😎",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("confirm_track_"))
async def handle_tracking_confirmation(callback: CallbackQuery):
    country_id, pizzeria_id = callback.data.split("_")[2:]
    
    async for session in db_manager.get_session():
        try:
            subscriptions = await get_user_subscriptions(session, callback.from_user.id)
            if any(s.pizzeria_id == pizzeria_id for s in subscriptions):
                await callback.answer("Вы уже подписаны на эту пиццерию! 😉", show_alert=True)
                return

            await add_subscription(
                session=session,
                user_id=callback.from_user.id,
                pizzeria_id=int(pizzeria_id),
                country_id=int(country_id)
            )
            
            await callback.answer(
                "Подписка оформлена! Теперь вы будете получать уведомления о доходах этой пиццерии 🎉",
                show_alert=True
            )

            await callback.data.set(f"pizzeria_{country_id}_{pizzeria_id}")
            await show_pizzeria_details(callback)
            
        except Exception as e:
            await callback.answer(
                "Произошла ошибка при подписке. Попробуйте позже 😔",
                show_alert=True
            )
            print(f"Subscription error for user {callback.from_user.id}: {e}")