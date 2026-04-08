"""数据库配置测试模块。"""

import pytest
from urllib.parse import urlparse

from app.config import Settings


class TestDatabaseConfig:
    """数据库配置测试类。"""

    def test_database_url_parsing(self):
        """测试数据库 URL 解析。"""
        # 模拟从环境变量加载的 URL
        database_url = "postgresql://user:password@localhost:5432/dm_assistant"

        parsed = urlparse(database_url)

        assert parsed.scheme == "postgresql"
        assert parsed.username == "user"
        assert parsed.password == "password"
        assert parsed.hostname == "localhost"
        assert parsed.port == 5432
        assert parsed.path == "/dm_assistant"

    def test_database_url_with_special_chars(self):
        """测试包含特殊字符的数据库 URL 解析。"""
        database_url = "postgresql://user:p%40ssw%40rd@localhost:5432/test_db"

        parsed = urlparse(database_url)

        assert parsed.username == "user"
        # 注意：urlparse 不会自动解码 URL 编码的密码
        assert "p%40ssw%40rd" in parsed.password or parsed.password == "p@ssw@rd"

    def test_config_loads_database_url(self):
        """测试配置类能加载数据库 URL。"""
        settings = Settings(
            database_url="postgresql://admin:secret123@127.0.0.1:5432/production_db"
        )

        assert settings.database_url == "postgresql://admin:secret123@127.0.0.1:5432/production_db"

    def test_empty_database_url(self):
        """测试空数据库 URL。"""
        settings = Settings()

        # 默认值为空字符串
        assert settings.database_url == ""

    def test_database_url_components_extraction(self):
        """测试提取数据库 URL 各组成部分。"""
        settings = Settings(
            database_url="postgresql://myuser:mypassword@192.168.1.100:5433/mydb"
        )

        parsed = urlparse(settings.database_url)

        config_info = {
            "scheme": parsed.scheme,
            "username": parsed.username,
            "password": parsed.password,
            "host": parsed.hostname,
            "port": parsed.port,
            "database": parsed.path.lstrip("/") if parsed.path else "",
        }

        assert config_info["scheme"] == "postgresql"
        assert config_info["username"] == "myuser"
        assert config_info["password"] == "mypassword"
        assert config_info["host"] == "192.168.1.100"
        assert config_info["port"] == 5433
        assert config_info["database"] == "mydb"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
