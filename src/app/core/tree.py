from fastapi import HTTPException, status
import httpx
import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.app.models import Tree
from src.app.utils.cache import UserCache



class TreeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_cache = UserCache()
        self.base_url = 'https://tumalas.kz/wp-admin/admin-ajax.php?action=tuma_cached_childnew_get&nodeid=14&id='
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }


    async def get_tree_on_api(self, id: int, parent_id: int):
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
                existing_node = await self.db.execute(select(Tree).where(Tree.t_id == t_id))
                if existing_node.scalars().first():
                    continue  # Пропускаем, если уже есть в БД

                new_node = Tree(
                    name=item['name'],
                    birth=item['birth_year'] if item['birth_year'] not in [None, 0] else None,
                    death=item['death_year'] if item['death_year'] not in [None, 0] else None,
                    parent_id=parent_id,
                    is_deleted=False,
                    t_id=t_id,
                    created_by=1,
                )

                self.db.add(new_node)
                new_nodes.append(new_node)

            if new_nodes:
                await self.db.commit()
            return new_nodes  # Возвращаем список добавленных узлов (может быть пустым)

        except Exception as e:
            logging.error(f"Ошибка при запросе дерева: {e}")
            return None  # Возвращаем None, если ошибка

    async def get_tree_on_db(self, node_id: int, user_id: int):
        result = await self.db.execute(select(Tree).where(Tree.id == node_id))
        node = result.scalars().first()
        if not node:
            raise HTTPException(status_code=404, detail='Node not found')

        # Проверяем, нет ли новых данных в API
        await self.get_tree_on_api(node.t_id, node_id)

        # После запроса к API делаем повторный запрос в БД (на случай обновлений)
        result = await self.db.execute(select(Tree).where(Tree.parent_id == node_id).order_by(Tree.id))
        childs = result.scalars().all()

        # role_id = await self.user_cache.get_user_role(user_id)

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
                    # "untouchable": True if role_id and role_id >= 2 else False,
                    "untouchable": False,
                    "mini_icon": child.mini_icon or None,  # Можно использовать `or`
                    "main_icon": child.main_icon or None,
                })
        return response

    async def delete_tree_on_page(self, node_id: int):
        result = await self.db.execute(select(Tree).where(Tree.id == node_id))
        node = result.scalars().first()
        if not node:
            raise HTTPException(status_code=404, detail='Node not found')
        node.is_deleted = True
        await self.db.commit()
        await self.db.refresh(node)
        return HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Сәтті жойылды")

    async def restore_tree_on_page(self, node_id: int):
        result = await self.db.execute(select(Tree).where(Tree.id == node_id))
        node = result.scalars().first()
        if not node:
            raise HTTPException(status_code=404, detail='Node not found')
        node.is_deleted = False
        await self.db.commit()
        await self.db.refresh(node)
        return HTTPException(status_code=status.HTTP_201_CREATED, detail="Сәтті қалпына келтірілді")

    async def search_data_by_name(self, name: str, parent_id: int = None):
        stmt = select(Tree).where(Tree.name.ilike(f"%{name}%"))
        result = await self.db.execute(stmt)
        response = []
        data = result.scalars().all()
        for res in data:
            if res.is_deleted:
                continue
            data = await self.get_parents(res.id, res.parent_id)
            if data == False:
                continue

            response.append({
                "id": res.id,
                "name": res.name,
                "birth": res.birth if res.birth else None,
                "death": res.death if res.death else None,
                "parents": data
            })  
        return response

    async def get_parents(self, tree_id: int, parent_id: int = None):
        parents = []
        current_id = tree_id

        while current_id is not None:
            stmt = select(Tree).where(Tree.id == current_id)
            result = await self.db.execute(stmt)
            node = result.scalar_one_or_none()

            if not node or node.parent_id is None:
                break

            stmt = select(Tree).where(Tree.id == node.parent_id)
            result = await self.db.execute(stmt)
            parent = result.scalar_one_or_none()

            if parent:
                parents.append({
                    "id": parent.id,
                    "name": parent.name,
                })
                current_id = parent.id
            else:
                break

        if not parents:
            return False

        # проверяем наличие конкретного предка
        if parent_id and not any(p["id"] == parent_id for p in parents):
            return False

        return parents[::-1]
    
    async def get_tree_data(self, node_id: int):
        result = await self.db.execute(
            select(Tree)
            .where(Tree.id == node_id)
            .options(
                selectinload(Tree.created_by_user),
                selectinload(Tree.updated_by_user)
            )
        )
        node = result.scalars().first()

        if not node:
            raise HTTPException(status_code=404, detail='Node not found')

        return {
            "id": node.id,
            "name": node.name,
            "mini_icon": node.mini_icon,
            "main_icon": node.main_icon,
            "birth": node.birth,
            "death": node.death,
            "bio": node.bio,
            "created_by": {
                "id": node.created_by_user.id if node.created_by_user else None,
                "first_name": node.created_by_user.first_name if node.created_by_user else None,
                "last_name": node.created_by_user.last_name if node.created_by_user else None,
            },
            "updated_by": {
                "id": node.updated_by_user.id if node.updated_by_user else None,
                "first_name": node.updated_by_user.first_name if node.updated_by_user else None,
                "last_name": node.updated_by_user.last_name if node.updated_by_user else None,
            }
        }
