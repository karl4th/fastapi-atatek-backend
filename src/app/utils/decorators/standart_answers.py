import inspect
from typing import Coroutine, Any, Callable
from functools import wraps
from fastapi import HTTPException
from src.app.config import settings


def standar_atatek(func: Coroutine) -> Callable[..., Coroutine[Any, Any, dict]]:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            data = await func(*args, **kwargs)
            return {
                "status": True,
                "api-version": settings.APP_VERSION,
                "data": data,
            }

        except HTTPException as e:
            # если вызывается FastAPI-ошибка — возвращаем в стандартизированном формате
            return {
                "status": False,
                "api-version": settings.APP_VERSION,
                "error": {
                    "code": e.status_code,
                    "message": e.detail,
                },
            }

        except Exception as e:
            # для всех остальных ошибок (например, RuntimeError)
            return {
                "status": False,
                "api-version": settings.APP_VERSION,
                "error": {
                    "code": 500,
                    "message": str(e),
                    "type": e.__class__.__name__,
                },
            }
        
        except:
            return {
                "status": False,
                "api-version": settings.APP_VERSION,
                "error": {
                    "code": 500,
                    "message": str(e),
                    "type": e.__class__.__name__,
                },
            }

    return wrapper
