"""Agent基类模块，定义所有Agent的通用接口。"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class BaseAgent(ABC, Generic[InputType, OutputType]):
    """
    Agent基类，所有具体Agent的抽象基类。

    定义了Agent的标准接口：
    - execute: 执行Agent的主要逻辑
    - build_prompt: 构建发送给LLM的提示词
    - parse_response: 解析LLM响应
    """

    name: str = "BaseAgent"
    description: str = "基础Agent"

    def __init__(self, llm_service: Any | None = None):
        """
        初始化Agent。

        Args:
            llm_service: LLM服务实例，用于调用大模型
        """
        self.llm_service = llm_service

    @abstractmethod
    async def execute(self, input_data: InputType) -> OutputType:
        """
        执行Agent的主要逻辑。

        Args:
            input_data: 输入数据

        Returns:
            输出数据
        """
        pass

    @abstractmethod
    def build_prompt(self, input_data: InputType) -> str:
        """
        构建发送给LLM的提示词。

        Args:
            input_data: 输入数据

        Returns:
            构建的提示词字符串
        """
        pass

    def parse_response(self, response: str) -> OutputType:
        """
        解析LLM的文本响应。

        默认实现直接返回字符串，子类可以覆盖此方法实现特定解析逻辑。

        Args:
            response: LLM的原始响应文本

        Returns:
            解析后的输出数据
        """
        return response  # type: ignore

    async def call_llm(
        self,
        prompt: str,
        system_prompt: str | None = None,
        json_mode: bool = False,
    ) -> str | dict[str, Any]:
        """
        调用LLM服务。

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            json_mode: 是否使用JSON模式

        Returns:
            LLM响应，可能是字符串或JSON对象

        Raises:
            RuntimeError: 如果LLM服务未配置
        """
        if not self.llm_service:
            raise RuntimeError(f"{self.name} 未配置LLM服务")

        if json_mode:
            return await self.llm_service.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
            )
        else:
            return await self.llm_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
            )
