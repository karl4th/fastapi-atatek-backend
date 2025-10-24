from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.config import auth
from src.app.db import get_db
from src.app.core import PageService
from src.app.schemas.page import (
    PageBase, 
    CreatePage, 
    UpdatePage,
    PageListResponse
)

from src.app.utils import standar_atatek


router = APIRouter(prefix="/pages", tags=['Pages'])


@router.get('/')
@standar_atatek
async def get_pages(
    limit: int = 10,
    offset: int = 0,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageService(db)
    result = await service.get_pages(skip=offset, limit=limit)
    return result

@router.get('/search')
@standar_atatek
async def search_pages(
    main_gen: int,
    main_gen_child: int | None = None,
    limit: int = 100,
    offset: int = 0,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageService(db)
    result = await service.search_pages(
        main_gen=main_gen,
        main_gen_child=main_gen_child,
        skip=offset,
        limit=limit
    )
    return result

@router.put('/set/page')
@standar_atatek
async def set_page_user(
    page_id: int,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageService(db)
    user_id = int(user_data['sub'])
    result = await service.set_page_user(
        user_id=user_id,
        page_id=page_id
    )
    return result


@router.post('/create')
@standar_atatek
async def create_page(
    payload: CreatePage,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageService(db)
    result =  await service.create_page(
        payload=payload
    )
    return result

@router.delete('/delete')
@standar_atatek
async def delete_page(
    page_id: int,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageService(db)
    result = await service.delete_page(
        page_id=page_id
    )
    return result

@router.put('/update')
@standar_atatek
async def update_page(  
    page_id: int,
    payload: UpdatePage,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageService(db)
    user_id = int(user_data['sub'])
    result = await service.update_page(
        user_id=user_id,
        page_id=page_id,
        payload=payload
    )
    return result

@router.post("/page/{page_id}/moderators/add")
@standar_atatek
async def add_moderator_to_page(
    page_id: int,
    user_id: int,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageService(db)
    result = await service.add_moderator(
        page_id=page_id,
        user_id=user_id
    )
    return result

@router.delete("/page/{page_id}/moderators/remove")
@standar_atatek
async def remove_moderator_from_page(
    moderator_id: int,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageService(db)
    result = await service.remove_moderator(
        moderator_id=moderator_id
    )
    return result

@router.get('/full/{page_id}')
@standar_atatek
async def get_full_page_by_id(
    page_id: int,
    user_data = Depends(auth.get_user_data_dependency()),
    db: AsyncSession = Depends(get_db)
):
    service = PageService(db)
    result = await service.get_page_by_id(page_id=page_id)
    return result