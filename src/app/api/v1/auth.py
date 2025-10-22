from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.config import auth
from src.app.db import get_db
from src.app.core import AuthService
from src.app.schemas.user import UserBase, CreateUser, VerifyUser, LoginUser
from src.app.utils import standar_atatek

router = APIRouter(prefix="/auth", tags=['Auth'])

@router.post("/signup")
@standar_atatek
async def create_user(payload:CreateUser, response: Response, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.create_user(payload=payload)
    access_token, refresh_token, csrf_token = auth.create_tokens(
        user.id,
    )
    auth.set_tokens_in_cookies(response, access_token, refresh_token, csrf_token)
    return user


@router.post("/signup/verify")
@standar_atatek
async def verify_user(payload: VerifyUser, user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user_id = int(user_data["sub"])
    return await service._toggle_verificate_user(user_id=user_id, payload=payload.verify_code)


@router.post('/signup/verify/send-code')
@standar_atatek
async def send_verify_cody(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user_id = int(user_data["sub"])
    return await service._get_verify_code(user_id=user_id)

@router.post('/singup/verify/resend')
@standar_atatek
async def resend_verify_code(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user_id = int(user_data["sub"])
    return await service._resend_verify_code(user_id=user_id)

@router.post('/login')
@standar_atatek
async def login_user(payload: LoginUser, response: Response, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    login = await service.login_user(payload)
    access_token, refresh_token, csrf_token = auth.create_tokens(
        login.id,
    )
    auth.set_tokens_in_cookies(response, access_token, refresh_token, csrf_token)
    return login

@router.get('/me')
@standar_atatek
async def login(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user_id = int(user_data['sub'])
    return await service.get_me(user_id)