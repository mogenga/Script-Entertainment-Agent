"""FastAPI 应用入口，配置路由和中间件。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理，启动时初始化数据库，关闭时清理连接。"""
    # 启动时执行
    await init_db()
    yield
    # 关闭时执行
    await close_db()


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.app_name,
    description="情感本DM演绎设计助手 API",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点，用于监控服务状态。"""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/", tags=["根路径"])
async def root():
    """根路径，返回 API 基本信息。"""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs_url": "/docs",
    }


# 导入并注册 API 路由
from app.api import performances_router, scripts_router

app.include_router(scripts_router, prefix="/api/v1")
app.include_router(performances_router, prefix="/api/v1")
