from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from ..core.config import settings


def setup_middleware(app):
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
