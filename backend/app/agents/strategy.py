"""改编策略Agent，分析环节内容并推荐演绎策略。"""

from dataclasses import dataclass

from app.agents.base import BaseAgent


@dataclass
class StrategyInput:
    """策略设计输入数据。"""

    episode_content: str
    """环节内容文本"""

    emotion_type: str
    """情感类型：爱情/亲情/友情/家国"""

    episode_type: str
    """环节类型：心建/羁绊仪式/情感爆发"""

    scene: str
    """具体场景"""

    characters: list[dict] | None = None
    """涉及的角色列表"""


@dataclass
class StrategySuggestion:
    """策略建议。"""

    approach: str
    """演绎手法"""

    key_moments: list[str]
    """关键情感节点"""

    interaction_points: list[str]
    """互动切入点"""


@dataclass
class StrategyOutput:
    """策略设计输出数据。"""

    analysis: str
    """环节分析"""

    target_emotion: str
    """目标情感"""

    suggestions: StrategySuggestion
    """策略建议"""

    recommended_duration: str
    """建议时长"""

    prop_suggestions: list[str]
    """道具建议"""


class StrategyDesignerAgent(BaseAgent[StrategyInput, StrategyOutput]):
    """
    改编策略Agent。

    分析环节内容，根据用户选择的维度推荐演绎策略。
    """

    name = "StrategyDesigner"
    description = "分析环节内容并推荐演绎策略"

    SYSTEM_PROMPT = """你是一个专业的剧本杀DM演绎策略设计师。
你的任务是根据环节内容和用户选择的维度，设计最佳的演绎策略。

你需要考虑：
1. 环节的情感核心是什么
2. 如何通过动作和互动强化情感表达
3. 什么道具可以增强沉浸感
4. 节奏的把控（何时停顿、何时推进）

输出必须是JSON格式：
{
    "analysis": "环节分析摘要",
    "target_emotion": "目标情感描述",
    "suggestions": {
        "approach": "推荐的演绎手法",
        "key_moments": ["关键情感节点1", "关键情感节点2"],
        "interaction_points": ["互动切入点1", "互动切入点2"]
    },
    "recommended_duration": "建议时长",
    "prop_suggestions": ["道具1", "道具2"]
}"""

    def build_prompt(self, input_data: StrategyInput) -> str:
        """构建策略分析提示词。"""
        characters_str = ""
        if input_data.characters:
            characters_str = "\n涉及角色:\n" + "\n".join(
                f"- {char.get('name', '未知')}: {char.get('description', '')}"
                for char in input_data.characters
            )

        return f"""请分析以下环节内容，设计演绎策略。

=== 用户选择的维度 ===
情感类型: {input_data.emotion_type}
环节类型: {input_data.episode_type}
具体场景: {input_data.scene}
{characters_str}

=== 环节内容 ===
{input_data.episode_content}
=== 环节内容结束 ===

请分析这个环节的情感核心，并给出具体的演绎策略建议。"""

    async def execute(self, input_data: StrategyInput) -> StrategyOutput:
        """执行策略设计。"""
        prompt = self.build_prompt(input_data)

        response = await self.call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            json_mode=True,
        )

        return self._parse_response(response)

    def _parse_response(self, response: dict | str) -> StrategyOutput:
        """解析响应。"""
        if isinstance(response, str):
            import json

            response = json.loads(response)

        suggestions_data = response.get("suggestions", {})
        suggestions = StrategySuggestion(
            approach=suggestions_data.get("approach", ""),
            key_moments=suggestions_data.get("key_moments", []),
            interaction_points=suggestions_data.get("interaction_points", []),
        )

        return StrategyOutput(
            analysis=response.get("analysis", ""),
            target_emotion=response.get("target_emotion", ""),
            suggestions=suggestions,
            recommended_duration=response.get("recommended_duration", "5-8分钟"),
            prop_suggestions=response.get("prop_suggestions", []),
        )
