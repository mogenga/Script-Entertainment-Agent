"""编排Agent，协调多Agent工作流，支持双轨对比模式。"""

from dataclasses import dataclass

from app.agents.base import BaseAgent
from app.agents.performance import PerformanceDesignerAgent, PerformanceInput, PerformanceOutput
from app.agents.strategy import StrategyDesignerAgent, StrategyInput, StrategyOutput


@dataclass
class OrchestratorInput:
    """编排器输入数据。"""

    episode_content: str
    """环节内容"""

    emotion_type: str
    """情感类型"""

    episode_type: str
    """环节类型"""

    scene: str
    """具体场景"""

    characters: list[dict] | None = None
    """角色列表"""

    user_idea: str | None = None
    """用户想法（协作模式时使用）"""


@dataclass
class PlanComparison:
    """方案对比分析。"""

    ai_strengths: list[str]
    """AI方案优点"""

    ai_suggestions: list[str]
    """AI方案改进建议"""

    user_strengths: list[str]
    """用户方案优点"""

    user_suggestions: list[str]
    """用户方案改进建议"""

    recommendation: str
    """综合建议"""


@dataclass
class OrchestratorOutput:
    """编排器输出数据。"""

    mode: str
    """模式：auto 或 collaborate"""

    ai_plan: PerformanceOutput
    """AI自动生成的方案"""

    user_plan: PerformanceOutput | None
    """基于用户想法的方案（仅协作模式）"""

    comparison: PlanComparison | None
    """对比分析（仅协作模式）"""


class OrchestratorAgent(BaseAgent[OrchestratorInput, OrchestratorOutput]):
    """
    编排Agent，协调StrategyDesigner和PerformanceDesigner的工作流。

    支持两种模式：
    - auto: 自动生成演绎方案
    - collaborate: 双轨生成（AI方案 + 用户方案）并对比分析
    """

    name = "Orchestrator"
    description = "协调多Agent工作流，支持双轨对比模式"

    def __init__(self, llm_service=None):
        """初始化编排Agent及其子Agent。"""
        super().__init__(llm_service)
        self.strategy_agent = StrategyDesignerAgent(llm_service)
        self.performance_agent = PerformanceDesignerAgent(llm_service)

    def build_prompt(self, input_data: OrchestratorInput) -> str:
        """编排器不需要直接调用LLM，此方法返回空字符串。"""
        return ""

    async def execute(self, input_data: OrchestratorInput) -> OrchestratorOutput:
        """
        执行编排逻辑。

        根据是否有user_idea决定使用auto模式还是collaborate模式。
        """
        if input_data.user_idea:
            return await self._execute_collaborate_mode(input_data)
        else:
            return await self._execute_auto_mode(input_data)

    async def _execute_auto_mode(self, input_data: OrchestratorInput) -> OrchestratorOutput:
        """自动模式：生成单一AI方案。"""
        # 第一步：生成策略
        strategy_input = StrategyInput(
            episode_content=input_data.episode_content,
            emotion_type=input_data.emotion_type,
            episode_type=input_data.episode_type,
            scene=input_data.scene,
            characters=input_data.characters,
        )
        strategy = await self.strategy_agent.execute(strategy_input)

        # 第二步：生成演绎方案
        performance_input = PerformanceInput(
            episode_content=input_data.episode_content,
            strategy=strategy,
            emotion_type=input_data.emotion_type,
            episode_type=input_data.episode_type,
            scene=input_data.scene,
            characters=input_data.characters,
        )
        performance = await self.performance_agent.execute(performance_input)

        return OrchestratorOutput(
            mode="auto",
            ai_plan=performance,
            user_plan=None,
            comparison=None,
        )

    async def _execute_collaborate_mode(
        self, input_data: OrchestratorInput
    ) -> OrchestratorOutput:
        """协作模式：生成双轨方案并对比。"""
        # 并行生成策略（AI策略和用户策略）
        ai_strategy_input = StrategyInput(
            episode_content=input_data.episode_content,
            emotion_type=input_data.emotion_type,
            episode_type=input_data.episode_type,
            scene=input_data.scene,
            characters=input_data.characters,
        )

        user_strategy_input = StrategyInput(
            episode_content=input_data.episode_content
            + f"\n\n=== DM的想法 ===\n{input_data.user_idea}\n=== 想法结束 ===",
            emotion_type=input_data.emotion_type,
            episode_type=input_data.episode_type,
            scene=input_data.scene,
            characters=input_data.characters,
        )

        # 生成两个策略
        ai_strategy = await self.strategy_agent.execute(ai_strategy_input)
        user_strategy = await self.strategy_agent.execute(user_strategy_input)

        # 生成两个演绎方案
        ai_performance_input = PerformanceInput(
            episode_content=input_data.episode_content,
            strategy=ai_strategy,
            emotion_type=input_data.emotion_type,
            episode_type=input_data.episode_type,
            scene=input_data.scene,
            characters=input_data.characters,
        )

        user_performance_input = PerformanceInput(
            episode_content=input_data.episode_content
            + f"\n\nDM的想法：{input_data.user_idea}",
            strategy=user_strategy,
            emotion_type=input_data.emotion_type,
            episode_type=input_data.episode_type,
            scene=input_data.scene,
            characters=input_data.characters,
        )

        ai_performance = await self.performance_agent.execute(ai_performance_input)
        user_performance = await self.performance_agent.execute(user_performance_input)

        # 生成对比分析
        comparison = await self._generate_comparison(
            ai_performance, user_performance, input_data.user_idea or ""
        )

        return OrchestratorOutput(
            mode="collaborate",
            ai_plan=ai_performance,
            user_plan=user_performance,
            comparison=comparison,
        )

    async def _generate_comparison(
        self,
        ai_plan: PerformanceOutput,
        user_plan: PerformanceOutput,
        user_idea: str,
    ) -> PlanComparison:
        """生成双轨方案对比分析。"""
        # 构建对比分析的提示词
        comparison_prompt = f"""请对比以下两个演绎方案，给出分析。

=== AI方案 ===
标题: {ai_plan.title}
时长: {ai_plan.duration}
步骤数: {len(ai_plan.steps)}
道具: {', '.join(ai_plan.props)}
注意事项: {ai_plan.notes}

=== 基于用户想法的方案 ===
用户原始想法: {user_idea}
标题: {user_plan.title}
时长: {user_plan.duration}
步骤数: {len(user_plan.steps)}
道具: {', '.join(user_plan.props)}
注意事项: {user_plan.notes}

请分析两个方案的优缺点，并给出建议。"""

        system_prompt = """你是剧本杀演绎设计专家。请对比两个演绎方案，给出客观分析。

输出必须是JSON格式：
{
    "ai_strengths": ["AI方案优点1", "AI方案优点2"],
    "ai_suggestions": ["AI方案改进建议1"],
    "user_strengths": ["用户方案优点1", "用户方案优点2"],
    "user_suggestions": ["用户方案改进建议1"],
    "recommendation": "综合建议"
}"""

        try:
            response = await self.call_llm(
                prompt=comparison_prompt,
                system_prompt=system_prompt,
                json_mode=True,
            )

            if isinstance(response, dict):
                return PlanComparison(
                    ai_strengths=response.get("ai_strengths", []),
                    ai_suggestions=response.get("ai_suggestions", []),
                    user_strengths=response.get("user_strengths", []),
                    user_suggestions=response.get("user_suggestions", []),
                    recommendation=response.get("recommendation", ""),
                )
        except Exception:
            # 如果LLM调用失败，返回默认对比
            pass

        # 默认对比结果
        return PlanComparison(
            ai_strengths=["结构化程度高", "易于执行"],
            ai_suggestions=["可增加更多情感细节"],
            user_strengths=["情感真挚", "有独特创意"],
            user_suggestions=["节奏可以更加紧凑"],
            recommendation="建议结合AI的结构化方案和你的情感表达。",
        )
