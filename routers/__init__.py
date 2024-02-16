__all__ = ("router",)

from aiogram import Router

from .admin_handlers import router as admin_router
from .common_handlers import router as common_router

router = Router(name=__name__)

router.include_routers(
    admin_router,
    common_router
)
