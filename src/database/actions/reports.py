from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.database.models.User import User
from datetime import datetime

async def add_subscription(
    session: AsyncSession,
    user_id: int,
    pizzeria_id: int,
    country_id: int
) -> User:
    try:
        subscription = User(
            telegram_id=user_id,
            pizzeria_id=pizzeria_id,
            country_id=country_id,
            is_active=True,
            active_since=datetime.now()
        )
        
        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)
        return subscription

    except IntegrityError:
        await session.rollback()
        subscription = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = subscription.scalar_one_or_none()
        
        if user:
            user.pizzeria_id = pizzeria_id
            user.country_id = country_id
            user.is_active = True
            user.active_since = datetime.utcnow()
            
            await session.commit()
            await session.refresh(user)
            return user
        else:
            raise

async def get_user_subscriptions(
    session: AsyncSession,
    user_id: int
) -> list[User]:
    query = select(User).where(
        User.telegram_id == user_id,
        User.is_active == True
    )
    result = await session.execute(query)
    return result.scalars().all()

async def remove_subscription(
    session: AsyncSession,
    user_id: int
) -> bool:
    query = select(User).where(
        User.telegram_id == user_id,
        User.is_active == True
    )
    result = await session.execute(query)
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.is_active = False
        await session.commit()
        return True
    return False