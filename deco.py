import asyncio
import inspect
from typing import  Coroutine
from functools import wraps
import asyncio
import inspect
import json
import logging
from functools import wraps
from typing import Callable, Coroutine

# --- CONFIGURE LOGGER ---
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# StreamHandler can be replaced by FileHandler or Loki handler later
handler = logging.StreamHandler()

# Loki prefers JSON logs
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def async_logger(func: Callable[..., Coroutine]):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        func_name = func.__name__
        args_json = {k: v for k, v in bound.arguments.items()}

        log_data = {
            "event": "function_call",
            "function": func_name,
            "args": args_json,
        }
        logger.info(json.dumps(log_data))

        try:
            result = await func(*args, **kwargs)
            log_data = {
                "event": "function_success",
                "function": func_name,
                "result": result,
            }
            logger.info(json.dumps(log_data))
            return result
        except Exception as e:
            log_data = {
                "event": "function_error",
                "function": func_name,
                "error_type": type(e).__name__,
                "error_message": str(e),
            }
            logger.error(json.dumps(log_data))
            raise

    return wrapper

async def check_func(func_name: str, user_id: int):
    print(f"Проверяем {func_name} для пользователя {user_id}")
    await asyncio.sleep(2)  # имитация запроса в БД
    return user_id == 1


def async_deco(func: Coroutine):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        user_id = bound.arguments.get('user_id')
        if await check_func(func.__name__, user_id):
            return await func(*args, **kwargs)
        else:
            return "Недостаточно прав"
        
    return wrapper


@async_logger
@async_deco
async def test_user(user_id: int, data: str):
    return f"Пользователь {user_id} получил доступ к {data}"


async def main():
    print(await test_user(12, "home"))
    # print(await test_user(2, "dashboard"))

asyncio.run(main())
