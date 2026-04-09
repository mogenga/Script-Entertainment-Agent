"""演绎方案相关数据模型。"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.script import Episode


class PerformanceStep(SQLModel, table=True):
    """演绎步骤模型，表示演绎手册中的一个步骤。"""

    __tablename__ = "performance_steps"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    performance_plan_id: UUID = Field(foreign_key="performance_plans.id", index=True)

    step_number: int = Field(description="步骤序号")
    action: str = Field(description="动作指令，如请玩家站起来")
    line: str = Field(description="DM台词")
    timing: Optional[str] = Field(default=None, description="节奏控制，如停顿3秒")
    music: Optional[str] = Field(default=None, description="背景音乐提示")


class PerformancePlan(SQLModel, table=True):
    """演绎方案模型，表示为一个环节生成的完整演绎手册。"""

    __tablename__ = "performance_plans"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    episode_id: UUID = Field(foreign_key="episodes.id", index=True)

    # 选择维度
    emotion_type: str = Field(description="情感类型：爱情/亲情/友情/家国")
    episode_type: str = Field(description="环节类型：心建/羁绊仪式/情感爆发")
    scene: str = Field(description="具体场景，如拜堂/对拜/递信物/回忆杀")

    # 生成内容
    title: str = Field(description="演绎方案标题")
    duration: str = Field(default="5-8分钟", description="预计时长")
    props: Optional[str] = Field(
        default=None, description="道具清单（JSON字符串数组）"
    )
    notes: Optional[str] = Field(default=None, description="注意事项")

    # 协作模式字段
    user_idea: Optional[str] = Field(default=None, description="DM提供的原始想法")
    ai_plan: Optional[str] = Field(
        default=None, description="AI自动生成的方案（JSON字符串）"
    )
    comparison: Optional[str] = Field(
        default=None, description="双轨对比分析（JSON字符串）"
    )
    is_collaborative: bool = Field(
        default=False, description="是否为协作模式生成的方案"
    )

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关联关系
    episode: "Episode" = Relationship(back_populates="performance_plans")
    steps: List["PerformanceStep"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
