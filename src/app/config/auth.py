from assem import AssemAUTH
from .config import settings


auth = AssemAUTH(
    secret_key=settings.JWT_SECRET_KEY,
    algo="HS256",
    access_token_expire_minutes=60,
    refresh_token_expire_days=7,
    secure_cookies=True,
    enable_csrf_protection=False,
)