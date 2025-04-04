from pathlib import Path

MEDIA_DIR = Path("frontend/static/picture").resolve()
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB