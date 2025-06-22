from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import logging
import os
from typing import AsyncGenerator
import asyncpg

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_session_maker = None
        
    async def init_database(self):
        try:
            DB_USER = os.getenv("PGUSER", "postgres")
            DB_PASS = os.getenv("PGPASSWORD", "postgres")
            DB_HOST = os.getenv("PGHOST", "db")
            DB_PORT = os.getenv("PGPORT", "5432")
            DB_NAME = os.getenv("PGNAME", "dodobot")

            DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

            try:
                conn = await asyncpg.connect(
                    user=DB_USER,
                    password=DB_PASS,
                    database=DB_NAME,
                    host=DB_HOST,
                    port=DB_PORT
                )
                await conn.close()
            except Exception as e:
                logger.error(f"Failed to connect to database: {str(e)}")
                logger.info("Please ensure PostgreSQL is running and the credentials are correct.")
                raise


            self.engine = create_async_engine(
                DATABASE_URL,
                echo=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
            )

            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise

    async def close_database(self):
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized")
            
        async with self.async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

db_manager = DatabaseManager()