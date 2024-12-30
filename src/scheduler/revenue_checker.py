import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.database.models.User import User
from src.services.dodo_api import DodoAPI
from src.models.revenue import CountryRevenue
from src.utils.formatting import get_currency_from_country_code
from typing import Optional
from pytz import timezone

logger = logging.getLogger(__name__)

class RevenueChecker:
    def __init__(
            self, 
            bot: Bot, 
            session_maker,
            dodo_api: DodoAPI
            ):
        self.bot = bot
        self.session_maker = session_maker
        self.dodo_api = dodo_api
        self.scheduler = AsyncIOScheduler(timezone=timezone('Asia/Oral'))
        self._running = False

    async def _get_revenue_data(self, country_id: int, pizzeria_id: str) -> Optional[float]:
        try:
            today = datetime.today()
            revenue = await self.dodo_api.get_daily_revenue(
                country_id, 
                pizzeria_id,
                today.year,
                today.month,
                today.day
                )
            if revenue is not None:
                print(revenue)
                if not revenue or not revenue[0].metrics:
                    return None

                # total_revenue = sum(
                #     metric.revenue
                #     for country in revenue
                #     for metric in country.metrics
                #     if metric.unitId == pizzeria_id
                # )
                
                return revenue

        except Exception as e:
            logger.error(f"Error getting revenue for pizzeria {pizzeria_id}: {e}")
            return None

    async def _format_message(self, revenue_data: CountryRevenue) -> str:
        if isinstance(revenue_data, list):
            if not revenue_data:
                return "No revenue data available"
            revenue_data = revenue_data[0]

        if not revenue_data.metrics:
            return "No revenue data available"
            
        metrics = revenue_data.metrics[0]
        currency = get_currency_from_country_code(revenue_data.countryCode)
        return (
            f"Ежедневый отчёт доходов вашей любимый пиццерии\n\n"
            f"💰 Общая выручка: {metrics.revenue:,.2f} {currency}\n"
            f"🏪 Касса: {metrics.stationaryRevenue:,.2f} {currency} ({metrics.stationaryCount} заказов)\n"
            f"🚚 Доставка: {metrics.deliveryRevenue:,.2f} {currency} ({metrics.deliveryCount} заказов)\n"
            f"🏃 Самовывоз: {metrics.pickupRevenue:,.2f} {currency} ({metrics.pickupCount} заказов)\n\n"
            f"📱 Заказы с приложения:\n"
            f"- Касса: {metrics.stationaryMobileRevenue:,.2f} {currency} ({metrics.stationaryMobileCount} заказов)\n"
            f"- Доставка: {metrics.deliveryMobileRevenue:,.2f} {currency} ({metrics.deliveryMobileCount} заказов)\n"
            f"- Самовывоз: {metrics.pickupMobileRevenue:,.2f} {currency} ({metrics.pickupMobileCount} заказов)"
        )

    def _reply_markup(self):
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Меню отслеживания",
            callback_data=f"userfollowingpizzeria"
        )
        return builder

    async def _notify_user(self, user: User, message: str) -> bool:
        try:
            await self.bot.send_message(
                user.telegram_id, 
                message, 
                reply_markup=self._reply_markup().as_markup()
                )
            return True
        except Exception as e:
            logger.error(f"Failed to send message to user {user.telegram_id}: {e}")
            return False

    async def _update_user_status(self, session: AsyncSession, user: User, active: bool):
        try:
            user.is_active = active
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to update user {user.telegram_id} status: {e}")
            await session.rollback()

    async def check_and_send_revenue(self):
        if not self._running:
            logger.warning("Scheduler is not running, skipping revenue check")
            return

        logger.info("Starting revenue check for all active users")
        async with self.session_maker() as session:
            try:
                query = select(User).filter(User.is_active == True)
                result = await session.execute(query)
                users = result.scalars().all()

                for user in users:
                    try:
                        revenue = await self._get_revenue_data(user.country_id, user.pizzeria_id)
                        if revenue is None:
                            logger.warning(f"No revenue data for user {user.telegram_id}")
                            continue

                        message = await self._format_message(revenue)
                        success = await self._notify_user(user, message)

                        if not success:
                            user.failed_notifications = (user.failed_notifications or 0) + 1
                            if user.failed_notifications >= 3:
                                await self._update_user_status(session, user, False)
                                logger.info(f"Deactivated user {user.telegram_id} due to failed notifications")
                        else:
                            user.failed_notifications = 0

                        await session.commit()

                    except Exception as e:
                        logger.error(f"Error processing user {user.telegram_id}: {e}")
                        await session.rollback()

            except Exception as e:
                logger.error(f"Error in revenue check main loop: {e}")

    def setup_scheduler(self, hour: int = 23, minute: int = 58, timezone = timezone('Asia/Oral')):
        try:
            self.scheduler.add_job(
                self.check_and_send_revenue,
                trigger=CronTrigger(
                    hour=hour, 
                    minute=minute, 
                    timezone=timezone
                    ),
                id='revenue_checker',
                replace_existing=True,
                misfire_grace_time=3600
            )
            self.scheduler.start()
            self._running = True
            logger.info(f"Revenue checker scheduled for {hour:02d}:{minute:02d}")
        except Exception as e:
            logger.error(f"Failed to setup scheduler: {e}")
            raise

    def stop_scheduler(self):
        try:
            self._running = False
            self.scheduler.shutdown()
            logger.info("Revenue checker scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")