from fastapi import APIRouter

from src.presentation.api.routers.books import router as books_router
from src.presentation.api.routers.config import router as config_router
from src.presentation.api.routers.queries import router as queries_router
from src.presentation.api.routers.status import router as status_router

router = APIRouter(prefix="/api/v1")
router.include_router(books_router)
router.include_router(queries_router)
router.include_router(config_router)
router.include_router(status_router)

__all__ = ["router"]
