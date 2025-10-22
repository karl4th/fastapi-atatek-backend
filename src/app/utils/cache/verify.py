from __future__ import annotations
import json
from typing import Any, Dict
from .redis import get_redis


class VerfiyCache():
    def __init__(self):
        self._DEFAULT_TTL = 180 
        self._KEY_PATTERN = "user:verify:{user_id}"

    async def get_user_code(self, user_id: int) -> Dict[str, Any]:
        r = await get_redis()
        key = self._KEY_PATTERN.format(user_id=user_id)

        if raw := await r.get(key):
            return json.loads(raw)

        return {"status": False, "details": "not found"}


    async def set_user_code(self, user_id: int, meta: Dict[str, Any],):
        r = await get_redis()
        delete = await self.invalidate(user_id=user_id)
        key = self._KEY_PATTERN.format(user_id=user_id)
        await r.set(key, json.dumps(meta), ex=self._DEFAULT_TTL)


    async def invalidate(self, user_id: int) -> None:
        """
        Удаляем данные из кэша
        """
        r = await get_redis()
        key = self._KEY_PATTERN.format(user_id=user_id)
        await r.delete(key)
    
