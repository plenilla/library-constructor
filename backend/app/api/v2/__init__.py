__all__ = (
    "contents_router",
    "exhibitions_router",
    "sections_router",
    "books_router",
    "library_books_router",
    "users_router",
    "admins_router",
)

from .contents.api import router as contents_router
from .exhibitions.api import router as exhibitions_router
from .sections.api import router as sections_router
from .books.api import router as books_router
from .books.api import router_library as library_books_router
from .users.api import router as users_router
from .users.api import admin_router as admins_router
