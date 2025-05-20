from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = Path("/storage/photos")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)