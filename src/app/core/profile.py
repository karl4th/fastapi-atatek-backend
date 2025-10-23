from src.app.schemas.profile import UpdateUser, ResetUserPasswort
from src.app.utils.cache import UserCache
from src.app.utils import AuthUtils
from src.app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import HTTPException, status

class ProfileService():
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache = UserCache()
        self.utils = AuthUtils()

    async def update_profile(self, user_id: int, payload: UpdateUser):
        stmp = await self.db.execute(select(User).where(User.id == user_id))
        user = stmp.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Қолданушы табылмады'
            )
        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.cache.invalidate(user_id=user_id)
        response = await self.cache.get_user_cache(user_id=user_id)
        return response
    
    async def update_password(self, user_id: int, payload: ResetUserPasswort):
        stmp = await self.db.execute(select(User).where(User.id == user_id))
        user = stmp.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Қолданушы табылмады'
            )
         
        if  self.utils.verify_password(payload.old_password, user.password) == False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ескі құпиясөз қате"
            )
    
        if payload.new_password != payload.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Құпиясөздер сәйкес келмейді"
            )
        
        password =  self.utils.hash_password(payload.new_password)
        user.password = password
        await self.db.commit()
        await self.db.refresh(user)

        response = await self.cache.get_user_cache(user_id=user_id)
        return response
    

    