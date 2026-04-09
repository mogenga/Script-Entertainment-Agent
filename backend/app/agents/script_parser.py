"""剧本解析Agent，将原始剧本文本解析为结构化数据。"""

from dataclasses import dataclass

from app.agents.base import BaseAgent


@dataclass
class ScriptParseInput:
    """剧本解析输入数据。"""

    content: str
    """原始剧本文本"""


@dataclass
class CharacterInfo:
    """角色信息。"""

    name: str
    description: str
    background: str


@dataclass
class EpisodeInfo:
    """环节信息。"""

    name: str
    content: str
    episode_type: str
    position: int


@dataclass
class ScriptParseOutput:
    """剧本解析输出数据。"""

    title: str
    characters: list[CharacterInfo]
    episodes: list[EpisodeInfo]


class ScriptParserAgent(BaseAgent[ScriptParseInput, ScriptParseOutput]):
    """
    剧本解析Agent。

    输入：原始剧本文本
    输出：结构化数据（标题、角色列表、环节列表）
    """

    name = "ScriptParser"
    description = "解析原始剧本文本，提取标题、角色和环节"

    SYSTEM_PROMPT = """你是一个专业的剧本杀剧本解析助手。
你的任务是从原始剧本文本中提取结构化信息。

请分析剧本内容，提取以下信息：
1. 剧本标题
2. 角色列表（每个角色包括：名称、描述、背景故事）
3. 环节列表（每个环节包括：名称、内容、类型、顺序位置）

环节类型必须是以下之一：
- narrative: 叙事/阅读环节
- interaction: 互动/演绎环节
- clue: 线索/搜证环节
- emotion: 情感/沉浸环节

你必须以JSON格式输出，格式如下：
{
    "title": "剧本标题",
    "characters": [
        {
            "name": "角色名",
            "description": "角色描述",
            "background": "角色背景故事"
        }
    ],
    "episodes": [
        {
            "name": "环节名称",
            "content": "环节内容摘要",
            "episode_type": "narrative/interaction/clue/emotion",
            "position": 0
        }
    ]
}"""

    def build_prompt(self, input_data: ScriptParseInput) -> str:
        """构建解析提示词。"""
        return f"""请解析以下剧本内容，提取标题、角色列表和环节列表。

=== 剧本内容 ===
{input_data.content}
=== 剧本内容结束 ===

请按照系统指令中的JSON格式输出解析结果。"""

    async def execute(self, input_data: ScriptParseInput) -> ScriptParseOutput:
        """执行剧本解析。"""
        prompt = self.build_prompt(input_data)

        # 调用LLM生成JSON响应
        response = await self.call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            json_mode=True,
        )

        # 解析响应
        return self._parse_json_response(response)

    def _parse_json_response(self, response: dict | str) -> ScriptParseOutput:
        """解析JSON响应为输出对象。"""
        if isinstance(response, str):
            import json

            response = json.loads(response)

        # 解析角色列表
        characters = [
            CharacterInfo(
                name=char["name"],
                description=char.get("description", ""),
                background=char.get("background", ""),
            )
            for char in response.get("characters", [])
        ]

        # 解析环节列表
        episodes = [
            EpisodeInfo(
                name=ep["name"],
                content=ep.get("content", ""),
                episode_type=ep.get("episode_type", "narrative"),
                position=ep.get("position", i),
            )
            for i, ep in enumerate(response.get("episodes", []))
        ]

        return ScriptParseOutput(
            title=response.get("title", "未命名剧本"),
            characters=characters,
            episodes=episodes,
        )
