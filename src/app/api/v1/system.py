from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.schemas.system import RoleCreate, RoleResponse, RolesList
from src.app.core.system import SystemService

router = APIRouter(prefix="/system", tags=["System"])

@router.post("", response_model=RoleResponse)
async def create_role(
    payload: RoleCreate,
    db: AsyncSession = Depends(get_db)
):
    service = SystemService(db)
    return await service.create_role(payload)

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int, db: AsyncSession = Depends(get_db)):
    service = SystemService(db)
    return await service.get_role_by_id(role_id)

@router.get("", response_model=RolesList)
async def list_roles(db: AsyncSession = Depends(get_db)):
    service = SystemService(db)
    return await service.get_roles()

@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    payload: RoleCreate,
    db: AsyncSession = Depends(get_db)
):
    service = SystemService(db)
    return await service.update_role(role_id, payload)

@router.delete("/{role_id}")
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    service = SystemService(db)
    return await service.delete_role(role_id)