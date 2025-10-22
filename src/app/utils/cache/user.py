from __future__ import annotations
import json
from typing import Any, Dict
from .redis import get_redis

from sqlalchemy import select
from src.app.models import User
from src.app.db import async_session_factory
from sqlalchemy.orm import selectinload
from src.app.schemas.user import UserFull


class UserCache:
    def __init__(self):
        self._DEFAULT_TTL = 600
        self._KEY_PATTERN = "user:meta:{user_id}"

    async def get_user_cache(self, user_id: int) -> Dict[str, Any]:
        """
        Получаем актуальные данные о пользователе из Redis
        """
        r = await get_redis()
        key = self._KEY_PATTERN.format(user_id=user_id)

        if raw := await r.get(key):
            return json.loads(raw)

        meta = await self._fetch_from_db(user_id)
        if meta:
            await self.set_user_data_on_cache(user_id, meta.model_dump())
            return meta.model_dump()

        return {"status": False, "details": "not found"}

    async def set_user_data_on_cache(self, user_id: int, meta: Dict[str, Any]):
        """
        Сохраняем данные пользователя в кэш
        """
        r = await get_redis()
        key = self._KEY_PATTERN.format(user_id=user_id)
        await r.set(key, json.dumps(meta), ex=self._DEFAULT_TTL)

    async def invalidate(self, user_id: int) -> None:
        """
        Удаляем данные из кэша
        """
        r = await get_redis()
        key = self._KEY_PATTERN.format(user_id=user_id)
        await r.delete(key)

    async def _fetch_from_db(self, user_id: int) -> UserFull | None:
        async with async_session_factory() as session:
            stmt = (
                select(User)
                .where(User.id == user_id, User.is_deleted.is_(False))
                .options(
                    selectinload(User.role),
                    selectinload(User.address),
                    selectinload(User.page),
                )
            )
            user = (await session.execute(stmt)).scalar_one_or_none()
            if not user:
                return None
            return UserFull.model_validate(user, from_attributes=True)
