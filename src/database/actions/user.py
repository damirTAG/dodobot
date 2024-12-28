from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models.User import User

async def get_user(
    session: AsyncSession,
    user_id: int,
) -> User:
    query = select(User).where(
        User.telegram_id == user_id,
    )
    result = await session.execute(query)
    return result.scalars().first()