from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.database.models.User import User
from src.utils.logger import logger

from typing import Optional

async def get_user(
    session: AsyncSession,
    user_id: int,
) -> Optional[User]:
    try:
        query = select(User).where(
            User.telegram_id == user_id,
        )
        result = await session.execute(query)
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user: {str(e)}")
        await session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching user: {str(e)}")
        await session.rollback()
        raise

async def add_user(
    session: AsyncSession,
    user_id: int,
    is_active: bool = False
) -> Optional[User]:
    try:
        query = insert(User).values(
            telegram_id=user_id,
            is_active=is_active
        )
        await session.execute(query)
        await session.commit()
        return await get_user(session, user_id)
        
    except IntegrityError as e:

        logger.error(f"User with telegram_id {user_id} already exists: {str(e)}")
        await session.rollback()

        existing_user = await get_user(session, user_id)
        if existing_user:
            return existing_user
        raise
        
    except SQLAlchemyError as e:

        logger.error(f"Database error while adding user: {str(e)}")
        await session.rollback()
        raise
        
    except Exception as e:

        logger.error(f"Unexpected error while adding user: {str(e)}")
        await session.rollback()
        raise

async def get_or_create_user(
    session: AsyncSession,
    user_id: int,
    is_active: bool = False
) -> Optional[User]:
    try:
        user = await get_user(session, user_id)
        if user is None:
            user = await add_user(session, user_id, is_active)
        logger.info(f'User {user_id} already exists')
        return user
        
    except Exception as e:
        print(f"Error in get_or_create_user: {str(e)}")
        raise