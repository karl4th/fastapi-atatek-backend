from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.app.db import get_db
from src.app.config.auth import auth
from src.app.core import TreeService
from src.app.utils import standar_atatek

router = APIRouter(prefix="/tree", tags=["National tree"])

@router.get('/')
@standar_atatek
async def get_tree(node_id: int, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = TreeService(db)
    return await service.get_tree_on_db(int(node_id), int(user_data["sub"]))


@router.get('/node/{node_id}')
@standar_atatek
async def get_node_data(node_id: int, user_data = Depends(auth.get_current_user_dependency()), db: AsyncSession = Depends(get_db)):
    service = TreeService(db)
    return await service.get_tree_data(node_id=node_id)


@router.delete('/node/{node_id}')
@standar_atatek
async def delete_node(node_id: int, user_data = Depends(auth.get_current_user_dependency()), db: AsyncSession = Depends(get_db)):
    service = TreeService(db)
    return await service.delete_tree_on_page(node_id=node_id)

@router.put('/node/{node_id}')
@standar_atatek
async def restore_node(node_id: int, user_data = Depends(auth.get_current_user_dependency()), db: AsyncSession = Depends(get_db)):
    service = TreeService(db)
    return await service.restore_tree_on_page(node_id=node_id)


@router.get('/search')
@standar_atatek
async def search_data_by_name(query: str, user_data = Depends(auth.get_current_user_dependency()), db: AsyncSession = Depends(get_db)):
    service = TreeService(db)
    return await service.search_data_by_name(name=query)
