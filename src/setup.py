import logging
from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv
from src.database.base import db_manager
from src.scheduler.revenue_checker import RevenueChecker
from src.services.dodo_api import DodoAPI
from src.handlers import register_handlers

logger = logging.getLogger(__name__)
load_dotenv('.env')

class BotApp:
    def __init__(self):
        self.bot = None
        self.dp = None
        self.dodo_api = None
        self.revenue_checker = None

    async def setup_services(self):
        try:
            logger.info("Initializing database...")
            await db_manager.init_database()

            logger.info("Setting up DodoAPI service...")
            self.dodo_api = DodoAPI()

            logger.info("Setting up revenue checker...")
            self.revenue_checker = RevenueChecker(
                bot=self.bot,
                session_maker=db_manager.async_session_maker,
                dodo_api=self.dodo_api
            )
            self.revenue_checker.setup_scheduler()
            
        except Exception as e:
            logger.error(f"Error during services setup: {e}")
            raise

    async def on_startup(self):
        try:
            await self.setup_services()
            logger.info("Bot startup completed!")
        except Exception as e:
            logger.error(f"Startup failed: {e}")
            raise

    async def on_shutdown(self):
        try:
            logger.info("Shutting down...")
            
            if self.revenue_checker:
                self.revenue_checker.stop_scheduler()
            
            await db_manager.close_database()
            
            logger.info("Shutdown completed!")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    async def start(self):
        self.bot = Bot(token=os.getenv("BOT_TOKEN"))
        self.dp = Dispatcher()
        
        self.dp.startup.register(self.on_startup)
        self.dp.shutdown.register(self.on_shutdown)
        
        try:
            logger.info("Starting bot...")
            register_handlers(self.dp)
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Bot stopped due to error: {e}")
            raise
        finally:
            if self.bot:
                await self.bot.session.close()