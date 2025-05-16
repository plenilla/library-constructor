from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / ".." / ".." / "frontend" / "public" / "picture"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
