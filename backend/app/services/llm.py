"""LLM服务模块，封装DashScope/Qwen API调用。"""

import json
import logging
from typing import Any, Optional

import dashscope
from dashscope import Generation

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务类，封装与Qwen模型的交互。"""

    def __init__(self):
        """初始化LLM服务。"""
        self.api_key = settings.dashscope_api_key
        self.model = settings.qwen_model or "qwen-max"
        self.temperature = settings.qwen_temperature

        # 设置DashScope API密钥
        if self.api_key:
            dashscope.api_key = self.api_key

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        生成文本响应。

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数（覆盖默认配置）
            max_tokens: 最大生成token数

        Returns:
            生成的文本响应

        Raises:
            RuntimeError: API调用失败时抛出
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = Generation.call(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens,
                result_format="message",
            )

            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                error_msg = f"LLM API调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        except Exception as e:
            error_msg = f"LLM服务异常: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        生成JSON格式的响应。

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数（覆盖默认配置）
            max_tokens: 最大生成token数

        Returns:
            解析后的JSON对象

        Raises:
            RuntimeError: API调用失败或JSON解析失败时抛出
        """
        # 在系统提示词中添加JSON输出要求
        json_system_prompt = system_prompt or ""
        json_system_prompt += (
            "\n\n重要：你必须以有效的JSON格式输出响应，不要包含任何其他文本。"
        )

        try:
            content = await self.generate(
                prompt=prompt,
                system_prompt=json_system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # 清理可能的markdown代码块标记
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # 解析JSON
            return json.loads(content)

        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败: {str(e)}"
            logger.error(f"{error_msg}\n原始内容: {content}")
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"JSON生成异常: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        聊天模式，支持多轮对话。

        Args:
            messages: 消息列表，格式为 [{"role": "user/system/assistant", "content": "..."}]
            temperature: 温度参数（覆盖默认配置）
            max_tokens: 最大生成token数

        Returns:
            生成的文本响应
        """
        try:
            response = Generation.call(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens,
                result_format="message",
            )

            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                error_msg = f"LLM Chat API调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        except Exception as e:
            error_msg = f"LLM Chat服务异常: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)


# 全局LLM服务实例
llm_service = LLMService()
