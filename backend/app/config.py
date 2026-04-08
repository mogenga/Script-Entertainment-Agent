"""应用配置模块，使用 Pydantic Settings 管理环境变量。"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类，从环境变量加载配置。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用配置
    app_name: str = "DM Assistant API"
    debug: bool = False

    # 数据库配置
    database_url: str = ""

    # Qwen API 配置（通过 DashScope）
    dashscope_api_key: str = ""
    qwen_model: str = ""
    qwen_temperature: float = 0.7

    # CORS 配置
    cors_origins: str = "http://localhost:3000,http://localhost:8081"

    # 安全配置
    secret_key: str = ""
    access_token_expire_minutes: int = 60

    @property
    def cors_origins_list(self) -> List[str]:
        """将 CORS 来源字符串解析为列表。"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# 全局配置实例
settings = Settings()
