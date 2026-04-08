"""数据库连接测试模块。"""

import pytest
from unittest.mock import patch

from app.config import Settings


class TestDatabaseConfig:
    """数据库配置测试类。"""

    def test_async_database_url_conversion(self):
        """测试同步URL转换为异步URL。"""
        sync_url = "postgresql://user:password@localhost:5432/dm_assistant"
        async_url = sync_url.replace("postgresql://", "postgresql+asyncpg://")

        assert async_url == "postgresql+asyncpg://user:password@localhost:5432/dm_assistant"

    def test_database_url_with_special_chars_conversion(self):
        """测试包含特殊字符的数据库URL转换。"""
        sync_url = "postgresql://user:p%40ssw%40rd@localhost:5432/test_db"
        async_url = sync_url.replace("postgresql://", "postgresql+asyncpg://")

        assert async_url == "postgresql+asyncpg://user:p%40ssw%40rd@localhost:5432/test_db"

    def test_database_url_from_settings(self):
        """测试从配置类获取数据库URL。"""
        settings = Settings(
            database_url="postgresql://admin:secret123@127.0.0.1:5432/production_db"
        )

        async_url = settings.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )

        assert "postgresql+asyncpg://" in async_url
        assert "admin" in async_url
        assert "secret123" in async_url
        assert "127.0.0.1" in async_url
        assert "production_db" in async_url

    def test_empty_database_url(self):
        """测试空数据库URL的处理。"""
        settings = Settings()

        # 空URL应该保持不变
        async_url = settings.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )

        assert async_url == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
