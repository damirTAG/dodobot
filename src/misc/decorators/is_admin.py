from functools import wraps
from typing import List, Callable, Any
from aiogram.types import Message, CallbackQuery
import os
from dotenv import load_dotenv

load_dotenv()

def get_admin_ids() -> List[int]:
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    try:
        return [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
    except ValueError as e:
        print(f"Error parsing ADMIN_IDS: {e}")
        return []

def admin_only() -> Callable:
    admin_ids = get_admin_ids()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(message: Message, *args: Any, **kwargs: Any) -> Any:
            if not admin_ids:
                await message.answer("Error: Admin IDs not configured")
                return

            if message.from_user.id not in admin_ids:
                await message.answer("Access denied: This command is for administrators only")
                return

            return await func(message, *args, **kwargs)
        return wrapper
    return decorator

# для кнопок
def admin_only_callback() -> Callable:
    admin_ids = get_admin_ids()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(callback: CallbackQuery, *args: Any, **kwargs: Any) -> Any:
            if not admin_ids:
                await callback.answer("Error: Admin IDs not configured", show_alert=True)
                return

            if callback.from_user.id not in admin_ids:
                await callback.answer("Access denied: Administrators only", show_alert=True)
                return

            return await func(callback, *args, **kwargs)
        return wrapper
    return decorator