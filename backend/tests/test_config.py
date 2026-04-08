"""配置模块测试。"""

import os
from unittest.mock import patch

import pytest

from app.config import Settings, settings


class TestSettings:
    """配置类测试套件。"""

    def test_default_values(self):
        """测试默认值设置是否正确。"""
        s = Settings()
        assert s.app_name == "DM Assistant API"
        assert s.debug is False
        assert s.qwen_model == "qwen-max"
        assert s.qwen_temperature == 0.7
        assert s.access_token_expire_minutes == 60

    def test_cors_origins_list_property(self):
        """测试 CORS 来源解析功能。"""
        s = Settings(cors_origins="http://localhost:3000, http://localhost:8081")
        assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:8081"]

    def test_cors_origins_single_value(self):
        """测试单个 CORS 来源值。"""
        s = Settings(cors_origins="http://localhost:3000")
        assert s.cors_origins_list == ["http://localhost:3000"]

    def test_custom_values_from_env(self):
        """测试从环境变量加载自定义值。"""
        env_vars = {
            "APP_NAME": "Test API",
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://test:test@localhost/test_db",
            "DASHSCOPE_API_KEY": "sk-test-key",
            "QWEN_MODEL": "qwen-turbo",
            "QWEN_TEMPERATURE": "0.5",
            "SECRET_KEY": "test-secret",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            s = Settings()
            assert s.app_name == "Test API"
            assert s.debug is True
            assert s.database_url == "postgresql://test:test@localhost/test_db"
            assert s.dashscope_api_key == "sk-test-key"
            assert s.qwen_model == "qwen-turbo"
            assert s.qwen_temperature == 0.5
            assert s.secret_key == "test-secret"
            assert s.access_token_expire_minutes == 30

    def test_global_settings_instance(self):
        """测试全局配置实例是否存在。"""
        assert isinstance(settings, Settings)
        assert settings.app_name is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
