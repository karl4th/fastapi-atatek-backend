# src/app/core/system.py
from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.app.models import Role
from src.app.schemas.system import RoleCreate, RoleResponse, RolesList


class SystemService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_role(self, payload: RoleCreate) -> RoleResponse:
        try:
            role = Role(name=payload.name, description=payload.description)
            self.db.add(role)
            await self.db.commit()
            await self.db.refresh(role)
            return RoleResponse.model_validate(role.__dict__)
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Ошибка создания роли")

    async def get_role_by_id(self, role_id: int) -> RoleResponse:
        try:
            res = await self.db.execute(select(Role).where(Role.id == role_id))
            role = res.scalar_one_or_none()
            if not role:
                raise HTTPException(status_code=404, detail="Роль не найдена")
            return RoleResponse.model_validate(role.__dict__)
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Ошибка получения роли")

    async def get_roles(self) -> RolesList:
        try:
            res = await self.db.execute(select(Role))
            roles: List[Role] = res.scalars().all()
            items = [RoleResponse.model_validate(r.__dict__) for r in roles]
            return RolesList(items=items, total=len(items))
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Ошибка получения списка ролей")

    async def update_role(self, role_id: int, payload: RoleCreate) -> RoleResponse:
        try:
            stmt = (
                update(Role)
                .where(Role.id == role_id)
                .values(name=payload.name, description=payload.description)
                .returning(Role)
            )
            res = await self.db.execute(stmt)
            role = res.scalar_one_or_none()
            if not role:
                raise HTTPException(status_code=404, detail="Роль не найдена")
            await self.db.flush()
            return RoleResponse.model_validate(role.__dict__)
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Ошибка обновления роли")

    async def delete_role(self, role_id: int) -> dict:
        try:
            stmt = delete(Role).where(Role.id == role_id).returning(Role.id)
            res = await self.db.execute(stmt)
            if res.scalar_one_or_none() is None:
                raise HTTPException(status_code=404, detail="Роль не найдена")
            return {"ok": True}
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Ошибка удаления роли")