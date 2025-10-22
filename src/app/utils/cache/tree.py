from __future__ import annotations
import json
from typing import Any, Dict
from .redis import get_redis
from fastapi import HTTPException
import httpx
import asyncio
from sqlalchemy import select
from src.app.models import Tree
from src.app.db import async_session_factory



class TreeCache:
    def __init__(self):
        self._DEFAULT_TTL = 600
        self._KEY_PATTERN = "tree:node:{node_id}"
        self.base_url = 'https://tumalas.kz/wp-admin/admin-ajax.php?action=tuma_cached_childnew_get&nodeid=14&id='
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }


    async def get_node(self, node_id: int) -> Dict[str, Any]:
        """
        Получаем актуальные данные о пользователе из Redis
        """
        r = await get_redis()
        key = self._KEY_PATTERN.format(node_id=node_id)

        if raw := await r.get(key):
            return json.loads(raw)

        meta = await self._fetch_from_db(node_id)
        if meta:
            await self.set_node(node_id, meta)
            return meta

        return {"status": False, "details": "not found"}

    async def set_node(self, node_id: int, meta: Dict[str, Any]):
        """
        Сохраняем данные пользователя в кэш
        """
        r = await get_redis()
        key = self._KEY_PATTERN.format(node_id=node_id)
        await r.set(key, json.dumps(meta), ex=self._DEFAULT_TTL)

    async def invalidate_node(self, node_id: int) -> None:
        """
        Удаляем данные из кэша
        """
        r = await get_redis()
        key = self._KEY_PATTERN.format(node_id=node_id)
        await r.delete(key)

    async def _fetch_from_db(self, node_id: int) -> dict | None:
        async with async_session_factory() as session:
            result = await session.execute(select(Tree).where(Tree.id == node_id))
            node = result.scalars().first()
            if not node:
                raise HTTPException(status_code=404, detail='Node not found')
            
            await self.get_tree_on_api(node.t_id, node_id, session)

            result = await session.execute(select(Tree).where(Tree.parent_id == node_id).order_by(Tree.id))
            childs = result.scalars().all()

            response = []
            if childs:
                for child in childs:
                    if child.is_deleted:
                        continue

                    response.append({
                        "id": child.id,
                        "name": child.name,
                        "birth": child.birth if child.birth else None,
                        "death": child.death if child.death else None,
                        "info": bool(child.bio),  # Более читабельная проверка
                        "untouchable": False,
                        "mini_icon": child.mini_icon or None,  # Можно использовать `or`
                        "main_icon": child.main_icon or None,
                    })
            return response
        
    async def get_tree_on_api(self, id: int, parent_id: int, session):
        url = f'{self.base_url}&id={id}'
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers=self.headers
                )
                response.raise_for_status()
            await asyncio.sleep(1)
            data = response.json()

            new_nodes = []
            for item in data:
                t_id = int(item['id'])

                # Проверяем, существует ли запись с таким t_id
                existing_node = await session.execute(select(Tree).where(Tree.t_id == t_id))
                if existing_node.scalars().first():
                    continue  # Пропускаем, если уже есть в БД

                new_node = Tree(
                    name=item['name'],
                    birth=item['birth_year'] if item['birth_year'] not in [None, 0] else None,
                    death=item['death_year'] if item['death_year'] not in [None, 0] else None,
                    parent_id=parent_id,
                    is_deleted=False,
                    t_id=t_id
                )

                session.add(new_node)
                new_nodes.append(new_node)

            if new_nodes:
                await session.commit()
            return new_nodes  # Возвращаем список добавленных узлов (может быть пустым)

        except Exception as e:
            return None  # Возвращаем None, если ошибка
