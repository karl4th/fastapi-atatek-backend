import inspect
from typing import  Coroutine
from functools import wraps


async def check_func(func_name: str, user_id: int):
    print(f"Проверяем {func_name} для пользователя {user_id}")
    return user_id == 1


def permission(func: Coroutine):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        user_id = bound.arguments.get('user_data')
        user_id = int(user_id['sub'])
        print(user_id)
        if await check_func(func.__name__, user_id):
            return await func(*args, **kwargs)
        else:
            return f"Недостаточно прав ID:{user_id} на {func.__name__}"
        
    return wrapper


