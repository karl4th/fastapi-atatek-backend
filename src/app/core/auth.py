# src/app/core/user.py
from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List
from src.app.utils import VerfiyCache, AuthUtils, UserCache

from src.app.models import User, UserSubscription
from src.app.schemas.user import CreateUser, UserResponse, UserBase, LoginUser, UserFull

class AuthService():

    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache = VerfiyCache()
        self.utils = AuthUtils()
        self.user_cache = UserCache()

    #================== HELPERS ==================#
    
    async def _get_user_by_id(self, user_id: int):
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Қолданушы табылмады")
        return user

    async def __get_user_by_phone(self, phone: int):
        result = await self.db.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Қолданушы табылмады")
        return user

    async def _toggle_verificate_user(self, user_id: int, payload: int):
        code = await self._get_verify_code(user_id=user_id)
        if code == payload:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Қолданушы табылмады")
            user.is_verified = True
            await self.db.commit()
            await self.db.refresh(user)
            await self.cache.invalidate(user_id=user_id)
            return {"detail": "Растау сәтті өтті"}

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сіз енгізген код қате немесе уақыты өтіп кеткен.")

    async def _get_verify_code(self, user_id: int):
        code = await self.cache.get_user_code(user_id)
        if code["status"] != False:
            code = int(code['code'])
            return code
        else: 
            return code
 
    async def _resend_verify_code(self, user_id: int):
        user = await self._get_user_by_id(user_id=user_id)
        if user.is_verified == True:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Бұл қолданушы телефон номерін растап қойған")
        meta = {"code": self.utils.generate_6_digit_code()}
        await self.cache.set_user_code(user_id=user_id, meta=meta)
        return {"detail": "Жаңа растау коды қайта жіберілді"}
    #================== MAIN FUNC ==================#

    async def create_user(self, payload: CreateUser):
        try:
            new_user = User(
                first_name=payload.first_name,
                last_name=payload.last_name,
                middle_name=payload.middle_name,
                phone=payload.phone,
                password=self.utils.hash_password(payload.password),
                role_id=1,
                address_id=None,
                page_id=None,
            )
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            meta = {"code": self.utils.generate_6_digit_code()}
            await self.cache.set_user_code(user_id=new_user.id, meta=meta)
            return UserBase.model_validate(new_user, from_attributes=True)

        except IntegrityError as e:
            await self.db.rollback()
            if "phone" in str(e.orig):
                raise HTTPException(status_code=409, detail="Бұл телефонмен тіркелген пайдаланушы бар")
            raise HTTPException(status_code=422, detail="Деректер дұрыс емес")

        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Тіркелу кезінде қателік орын алды")

    async def login_user(self, payload: LoginUser):
        user = await self.__get_user_by_phone(payload.phone)
        if self.utils.verify_password(payload.password, user.password):
            return UserResponse.model_validate(user.__dict__)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Телефон номер немесе құпиясөз қате"
            )
        
    async def get_me(self, user_id: int) -> UserFull:
        data = await self.user_cache.get_user_cache(user_id=user_id)
        return data
        
