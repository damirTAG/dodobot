from functools import wraps

from src.database.actions.user import get_or_create_user
from src.database.base import db_manager

from typing import Callable, Any
from src.utils.logger import logger

def is_new_user() -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(message: Any, *args: Any, **kwargs: Any) -> Any:
            async for session in db_manager.get_session():
                try:
                    user_id = message.from_user.id

                    logger.info(f'Adding new user... {user_id}')
                    await get_or_create_user(session, user_id)

                    return await func(message, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    raise
        return wrapper
    return decorator