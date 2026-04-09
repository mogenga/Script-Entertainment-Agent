"""演绎设计Agent，生成完整的演绎手册。"""

from dataclasses import dataclass

from app.agents.base import BaseAgent
from app.agents.strategy import StrategyOutput


@dataclass
class PerformanceInput:
    """演绎设计输入数据。"""

    episode_content: str
    """环节内容"""

    strategy: StrategyOutput
    """策略建议"""

    emotion_type: str
    """情感类型"""

    episode_type: str
    """环节类型"""

    scene: str
    """具体场景"""

    characters: list[dict] | None = None
    """角色列表"""


@dataclass
class PerformanceStep:
    """演绎步骤。"""

    step_number: int
    action: str
    line: str
    timing: str | None
    music: str | None


@dataclass
class PerformanceOutput:
    """演绎设计输出数据。"""

    title: str
    """方案标题"""

    duration: str
    """预计时长"""

    steps: list[PerformanceStep]
    """演绎步骤列表"""

    props: list[str]
    """道具清单"""

    notes: str
    """注意事项"""


class PerformanceDesignerAgent(BaseAgent[PerformanceInput, PerformanceOutput]):
    """
    演绎设计Agent。

    基于策略输出完整的演绎手册（动作、台词、节奏、道具）。
    """

    name = "PerformanceDesigner"
    description = "生成完整的演绎手册"

    SYSTEM_PROMPT = """你是一个专业的剧本杀DM演绎设计师。
你的任务是根据策略建议，设计详细的演绎手册。

演绎手册需要包含：
1. 步骤编号
2. 动作指令（DM要做什么）
3. DM台词（说什么）
4. 节奏控制（何时停顿、语速等）
5. 背景音乐提示

每个步骤都要具体可执行，台词要富有情感但不矫情。

输出必须是JSON格式：
{
    "title": "演绎方案标题",
    "duration": "预计时长",
    "steps": [
        {
            "step_number": 1,
            "action": "动作指令",
            "line": "DM台词",
            "timing": "节奏控制（可为null）",
            "music": "音乐提示（可为null）"
        }
    ],
    "props": ["道具1", "道具2"],
    "notes": "注意事项"
}"""

    def build_prompt(self, input_data: PerformanceInput) -> str:
        """构建演绎设计提示词。"""
        strategy = input_data.strategy

        characters_str = ""
        if input_data.characters:
            characters_str = "\n角色:\n" + "\n".join(
                f"- {char.get('name', '未知')}" for char in input_data.characters
            )

        return f"""请根据以下策略建议，设计详细的演绎手册。

=== 维度选择 ===
情感类型: {input_data.emotion_type}
环节类型: {input_data.episode_type}
场景: {input_data.scene}
{characters_str}

=== 环节内容 ===
{input_data.episode_content}

=== 策略建议 ===
目标情感: {strategy.target_emotion}
演绎手法: {strategy.suggestions.approach}
关键节点: {', '.join(strategy.suggestions.key_moments)}
互动切入点: {', '.join(strategy.suggestions.interaction_points)}
建议时长: {strategy.recommended_duration}
建议道具: {', '.join(strategy.prop_suggestions)}
=== 策略结束 ===

请设计详细的演绎手册，包含具体的动作、台词和节奏控制。"""

    async def execute(self, input_data: PerformanceInput) -> PerformanceOutput:
        """执行演绎设计。"""
        prompt = self.build_prompt(input_data)

        response = await self.call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            json_mode=True,
        )

        return self._parse_response(response)

    def _parse_response(self, response: dict | str) -> PerformanceOutput:
        """解析响应。"""
        if isinstance(response, str):
            import json

            response = json.loads(response)

        steps_data = response.get("steps", [])
        steps = [
            PerformanceStep(
                step_number=step.get("step_number", i + 1),
                action=step.get("action", ""),
                line=step.get("line", ""),
                timing=step.get("timing"),
                music=step.get("music"),
            )
            for i, step in enumerate(steps_data)
        ]

        return PerformanceOutput(
            title=response.get("title", "演绎方案"),
            duration=response.get("duration", "5-8分钟"),
            steps=steps,
            props=response.get("props", []),
            notes=response.get("notes", ""),
        )
