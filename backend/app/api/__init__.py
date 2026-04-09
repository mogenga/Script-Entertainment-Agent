"""API路由模块，包含所有FastAPI路由。"""

from app.api.performances import router as performances_router
from app.api.scripts import router as scripts_router

__all__ = ["scripts_router", "performances_router"]
