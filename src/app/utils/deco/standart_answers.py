import inspect
from typing import Coroutine, Any, Callable
from functools import wraps
from fastapi import HTTPException


def standar_atatek(func: Coroutine) -> Callable[..., Coroutine[Any, Any, dict]]:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            data = await func(*args, **kwargs)
            return {
                "status": True,
                "data": data,
            }

        except HTTPException as e:
            # если вызывается FastAPI-ошибка — возвращаем в стандартизированном формате
            return {
                "status": False,
                "error": {
                    "code": e.status_code,
                    "message": e.detail,
                },
            }

        except Exception as e:
            # для всех остальных ошибок (например, RuntimeError)
            return {
                "status": False,
                "error": {
                    "code": 500,
                    "message": str(e),
                    "type": e.__class__.__name__,
                },
            }
        
        except:
            return {
                "status": False,
                "error": {
                    "code": 500,
                    "message": str(e),
                    "type": e.__class__.__name__,
                },
            }

    return wrapper
