"""数据库连接模块，配置SQLModel引擎和会话管理。"""

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings

# 导入所有模型以确保SQLModel.metadata包含所有表
# noqa: F401 - 导入仅用于注册模型
from app.models import Character, CharacterRelationship, Episode, PerformancePlan, PerformanceStep, Script  # noqa: F401

# 创建异步引擎
# 将postgresql://替换为postgresql+asyncpg://以支持异步
async_database_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    async_database_url,
    echo=settings.debug,  # 调试模式下输出SQL语句
    future=True,
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_pre_ping=True,  # 连接前ping测试，避免使用已断开的连接
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """初始化数据库，创建所有表。"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """关闭数据库连接。"""
    await engine.dispose()


async def get_session():
    """获取数据库会话的依赖函数。"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
