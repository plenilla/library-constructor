__all__ = ("Base", "get_db", "BASE_DIR", "MEDIA_DIR", "settings", "templates")

from .database import get_db, settings
from .img import BASE_DIR, MEDIA_DIR
from .pages import templates

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
