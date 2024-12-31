from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods.get_chat import GetChat

from src.database.actions.user import get_all_users, get_user
from src.database.base import db_manager
from src.utils.paginate import paginate_keyboard
from src.utils.logger import logger
from src.misc.decorators.is_admin import admin_only, admin_only_callback

router = Router()

@router.message(Command("users"))
@admin_only()
async def list_users(message: Message):
    async for session in db_manager.get_session():
        try:
            users = await get_all_users(session)

            if not users:
                await message.reply("Нет пользователей.")
                return
            markup = paginate_keyboard(users, 0, "user")
            await message.reply("Список пользователей:", reply_markup=markup)

        except Exception as e:
            await message.reply("Ошибка при получении списка пользователей.")
            logger.error(f"SQLAlchemyError: {e}")


@router.callback_query(lambda c: c.data.startswith("user_"))
async def show_user_details(callback: CallbackQuery):
    telegram_id = int(callback.data.split("_")[1])
    # print(telegram_id)

    async for session in db_manager.get_session():
        try:
            user = await get_user(session, telegram_id)
            # full_name = await 

            if not user:
                await callback.message.edit_text("Пользователь не найден.")
                return

            builder = InlineKeyboardBuilder()
            builder.button(
                text='К юзерам',
                callback_data='back_to_users'
            )

            user_details = (
                f"ID: {user.id}\n"
                f"Telegram ID: {user.telegram_id}\n"
                # f"Full name: {full_name}\n"
                f"Country ID: {user.country_id}\n"
                f"Pizzeria ID: {user.pizzeria_id}\n"
                f"Active: {'Yes' if user.is_active else 'No'}\n"
                f"Active Since: {user.active_since}\n"
                f"Failed Notifications: {user.failed_notifications}\n"
                f"Notification Time: {user.notification_time}\n"
                f"Created At: {user.created_at}\n"
                f"Updated At: {user.updated_at}"
            )

            await callback.message.edit_text(user_details, reply_markup=builder.as_markup())

        except Exception as e:
            await callback.message.edit_text("Ошибка при получении данных пользователя.")
            logger.error(f"Error users: {e}")

@router.callback_query(F.data.startswith("page_user_"))
async def process_city_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    async for session in db_manager.get_session():
        users = await get_all_users(session)
        keyboard = paginate_keyboard(users, int(page), "user")
        await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "back_to_users")
async def back_to_users(callback: CallbackQuery):
    try:
        async for session in db_manager.get_session():
            users = await get_all_users(session)

            if not users:
                await callback.message.edit_text("Нет пользователей.")
                return

            keyboard = paginate_keyboard(users, 0, "user")

            await callback.message.edit_text("Список пользователей:", reply_markup=keyboard)

    except Exception as e:
        await callback.message.edit_text("Ошибка при получении списка пользователей.")
        logger.error(f"Exception: {e}")