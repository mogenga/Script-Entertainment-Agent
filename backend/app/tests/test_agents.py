"""Agent单元测试。"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents import (
    OrchestratorAgent,
    PerformanceDesignerAgent,
    ScriptParserAgent,
    StrategyDesignerAgent,
)
from app.agents.orchestrator import OrchestratorInput, OrchestratorOutput
from app.agents.performance import PerformanceInput, PerformanceOutput, PerformanceStep
from app.agents.script_parser import ScriptParseInput, ScriptParseOutput
from app.agents.strategy import StrategyInput, StrategyOutput, StrategySuggestion


# ==================== BaseAgent Tests ====================

class TestBaseAgent:
    """BaseAgent基础测试。"""

    def test_agent_initialization(self):
        """测试Agent初始化。"""
        mock_llm = MagicMock()
        agent = ScriptParserAgent(mock_llm)
        assert agent.llm_service == mock_llm
        assert agent.name == "ScriptParser"

    async def test_call_llm_without_service(self):
        """测试未配置LLM服务时抛出异常。"""
        agent = ScriptParserAgent(None)
        with pytest.raises(RuntimeError, match="未配置LLM服务"):
            await agent.call_llm("test prompt")


# ==================== ScriptParserAgent Tests ====================

class TestScriptParserAgent:
    """ScriptParserAgent测试。"""

    @pytest.fixture
    def mock_llm(self):
        """创建模拟LLM服务。"""
        llm = AsyncMock()
        llm.generate_json = AsyncMock(return_value={
            "title": "测试剧本",
            "characters": [
                {"name": "角色A", "description": "描述A", "background": "背景A"},
                {"name": "角色B", "description": "描述B", "background": "背景B"},
            ],
            "episodes": [
                {"name": "序幕", "content": "开场", "episode_type": "narrative", "position": 0},
                {"name": "第一幕", "content": "发展", "episode_type": "interaction", "position": 1},
            ],
        })
        return llm

    @pytest.fixture
    def agent(self, mock_llm):
        """创建测试用的Agent实例。"""
        return ScriptParserAgent(mock_llm)

    @pytest.mark.asyncio
    async def test_execute_success(self, agent, mock_llm):
        """测试正常解析流程。"""
        input_data = ScriptParseInput(content="这是一个测试剧本...")

        result = await agent.execute(input_data)

        assert isinstance(result, ScriptParseOutput)
        assert result.title == "测试剧本"
        assert len(result.characters) == 2
        assert len(result.episodes) == 2
        assert result.characters[0].name == "角色A"
        assert result.episodes[0].name == "序幕"

        # 验证LLM被调用
        mock_llm.generate_json.assert_called_once()

    def test_build_prompt(self, agent):
        """测试提示词构建。"""
        input_data = ScriptParseInput(content="测试内容")
        prompt = agent.build_prompt(input_data)

        assert "测试内容" in prompt
        assert "剧本内容" in prompt


# ==================== StrategyDesignerAgent Tests ====================

class TestStrategyDesignerAgent:
    """StrategyDesignerAgent测试。"""

    @pytest.fixture
    def mock_llm(self):
        """创建模拟LLM服务。"""
        llm = AsyncMock()
        llm.generate_json = AsyncMock(return_value={
            "analysis": "这是一个感人的离别场景",
            "target_emotion": "依依惜别的爱情",
            "suggestions": {
                "approach": "使用信物传递来强化情感",
                "key_moments": ["递信物", "眼神交汇"],
                "interaction_points": ["询问玩家感受", "引导玩家说出心里话"],
            },
            "recommended_duration": "6-8分钟",
            "prop_suggestions": ["玉佩", "书信"],
        })
        return llm

    @pytest.fixture
    def agent(self, mock_llm):
        """创建测试用的Agent实例。"""
        return StrategyDesignerAgent(mock_llm)

    @pytest.mark.asyncio
    async def test_execute_success(self, agent, mock_llm):
        """测试正常策略生成流程。"""
        input_data = StrategyInput(
            episode_content="你们即将分别...",
            emotion_type="爱情",
            episode_type="羁绊仪式",
            scene="递信物告别",
            characters=[{"name": "李明", "description": "男主角"}],
        )

        result = await agent.execute(input_data)

        assert isinstance(result, StrategyOutput)
        assert result.analysis == "这是一个感人的离别场景"
        assert result.target_emotion == "依依惜别的爱情"
        assert result.suggestions.approach == "使用信物传递来强化情感"
        assert len(result.suggestions.key_moments) == 2
        assert result.recommended_duration == "6-8分钟"

    def test_build_prompt(self, agent):
        """测试提示词构建。"""
        input_data = StrategyInput(
            episode_content="测试内容",
            emotion_type="爱情",
            episode_type="情感爆发",
            scene="测试场景",
        )
        prompt = agent.build_prompt(input_data)

        assert "测试内容" in prompt
        assert "爱情" in prompt
        assert "测试场景" in prompt


# ==================== PerformanceDesignerAgent Tests ====================

class TestPerformanceDesignerAgent:
    """PerformanceDesignerAgent测试。"""

    @pytest.fixture
    def mock_llm(self):
        """创建模拟LLM服务。"""
        llm = AsyncMock()
        llm.generate_json = AsyncMock(return_value={
            "title": "告别信物演绎方案",
            "duration": "6-8分钟",
            "steps": [
                {
                    "step_number": 1,
                    "action": "请玩家闭上眼睛",
                    "line": "现在，想象你就站在那棵樱花树下...",
                    "timing": "停顿2秒",
                    "music": "轻柔钢琴曲",
                },
                {
                    "step_number": 2,
                    "action": "递出玉佩",
                    "line": "这是TA留给你的...",
                    "timing": None,
                    "music": None,
                },
            ],
            "props": ["玉佩", "樱花花瓣"],
            "notes": "注意情感递进，不要急于求成",
        })
        return llm

    @pytest.fixture
    def agent(self, mock_llm):
        """创建测试用的Agent实例。"""
        return PerformanceDesignerAgent(mock_llm)

    @pytest.fixture
    def mock_strategy(self):
        """创建模拟策略输出。"""
        return StrategyOutput(
            analysis="离别场景",
            target_emotion="依依惜别",
            suggestions=StrategySuggestion(
                approach="信物传递",
                key_moments=["递信物"],
                interaction_points=["询问感受"],
            ),
            recommended_duration="6-8分钟",
            prop_suggestions=["玉佩"],
        )

    @pytest.mark.asyncio
    async def test_execute_success(self, agent, mock_llm, mock_strategy):
        """测试正常演绎设计流程。"""
        input_data = PerformanceInput(
            episode_content="你们即将分别...",
            strategy=mock_strategy,
            emotion_type="爱情",
            episode_type="羁绊仪式",
            scene="递信物告别",
        )

        result = await agent.execute(input_data)

        assert isinstance(result, PerformanceOutput)
        assert result.title == "告别信物演绎方案"
        assert len(result.steps) == 2
        assert result.steps[0].step_number == 1
        assert result.steps[0].action == "请玩家闭上眼睛"
        assert result.props == ["玉佩", "樱花花瓣"]

    def test_build_prompt(self, agent, mock_strategy):
        """测试提示词构建。"""
        input_data = PerformanceInput(
            episode_content="测试内容",
            strategy=mock_strategy,
            emotion_type="爱情",
            episode_type="羁绊仪式",
            scene="测试场景",
        )
        prompt = agent.build_prompt(input_data)

        assert "测试内容" in prompt
        assert "依依惜别" in prompt
        assert "信物传递" in prompt


# ==================== OrchestratorAgent Tests ====================

class TestOrchestratorAgent:
    """OrchestratorAgent测试。"""

    @pytest.fixture
    def mock_strategy_agent(self):
        """创建模拟策略Agent。"""
        agent = AsyncMock()
        agent.execute = AsyncMock(return_value=StrategyOutput(
            analysis="分析",
            target_emotion="情感",
            suggestions=StrategySuggestion(
                approach="手法",
                key_moments=["节点"],
                interaction_points=["互动"],
            ),
            recommended_duration="5分钟",
            prop_suggestions=["道具"],
        ))
        return agent

    @pytest.fixture
    def mock_performance_agent(self):
        """创建模拟演绎Agent。"""
        agent = AsyncMock()
        agent.execute = AsyncMock(return_value=PerformanceOutput(
            title="测试方案",
            duration="5分钟",
            steps=[PerformanceStep(
                step_number=1,
                action="动作",
                line="台词",
                timing=None,
                music=None,
            )],
            props=["道具"],
            notes="注意",
        ))
        return agent

    @pytest.fixture
    def agent(self, mock_strategy_agent, mock_performance_agent):
        """创建测试用的Agent实例。"""
        agent = OrchestratorAgent(None)
        agent.strategy_agent = mock_strategy_agent
        agent.performance_agent = mock_performance_agent
        return agent

    @pytest.mark.asyncio
    async def test_auto_mode(self, agent):
        """测试自动模式。"""
        input_data = OrchestratorInput(
            episode_content="测试内容",
            emotion_type="爱情",
            episode_type="羁绊仪式",
            scene="测试场景",
        )

        result = await agent.execute(input_data)

        assert isinstance(result, OrchestratorOutput)
        assert result.mode == "auto"
        assert result.ai_plan is not None
        assert result.user_plan is None
        assert result.comparison is None

    @pytest.mark.asyncio
    async def test_collaborate_mode(self, agent):
        """测试协作模式。"""
        input_data = OrchestratorInput(
            episode_content="测试内容",
            emotion_type="爱情",
            episode_type="羁绊仪式",
            scene="测试场景",
            user_idea="我想用烛光来营造氛围",
        )

        result = await agent.execute(input_data)

        assert isinstance(result, OrchestratorOutput)
        assert result.mode == "collaborate"
        assert result.ai_plan is not None
        assert result.user_plan is not None
        assert result.comparison is not None
