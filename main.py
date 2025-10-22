from fastapi import FastAPI
from src.app.config import settings
from src.app.api.v1 import include_routers


app = FastAPI(
    version=settings.APP_VERSION,
    title="Atatek API",
    description="New version on Atatek API using FastAPI",
)


include_routers(app)