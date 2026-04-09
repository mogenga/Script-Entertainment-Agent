"""Pydantic Schemas，用于请求和响应数据验证。"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==================== 基础响应 ====================

class BaseResponse(BaseModel):
    """基础响应模型。"""

    success: bool = True
    message: Optional[str] = None


# ==================== 角色相关 ====================

class CharacterBase(BaseModel):
    """角色基础模型。"""

    name: str = Field(description="角色名称")
    description: Optional[str] = Field(default=None, description="角色描述")
    background: Optional[str] = Field(default=None, description="角色背景故事")


class CharacterCreate(CharacterBase):
    """创建角色请求模型。"""

    pass


class CharacterResponse(CharacterBase):
    """角色响应模型。"""

    id: UUID
    script_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 角色关系相关 ====================

class CharacterRelationshipBase(BaseModel):
    """角色关系基础模型。"""

    source_id: UUID = Field(description="源角色ID")
    target_id: UUID = Field(description="目标角色ID")
    relationship_type: str = Field(description="关系类型")
    description: Optional[str] = Field(default=None, description="关系描述")


class CharacterRelationshipCreate(CharacterRelationshipBase):
    """创建角色关系请求模型。"""

    pass


class CharacterRelationshipResponse(CharacterRelationshipBase):
    """角色关系响应模型。"""

    id: int

    class Config:
        from_attributes = True


# ==================== 环节相关 ====================

class EpisodeBase(BaseModel):
    """环节基础模型。"""

    name: str = Field(description="环节名称")
    content: str = Field(description="环节内容文本")
    episode_type: str = Field(default="narrative", description="环节类型")
    position: int = Field(default=0, description="环节顺序位置")


class EpisodeCreate(EpisodeBase):
    """创建环节请求模型。"""

    pass


class EpisodeResponse(EpisodeBase):
    """环节响应模型。"""

    id: UUID
    script_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EpisodeListResponse(BaseModel):
    """环节列表响应模型。"""

    episodes: List[EpisodeResponse]


# ==================== 剧本相关 ====================

class ScriptBase(BaseModel):
    """剧本基础模型。"""

    title: str = Field(description="剧本标题")
    content: str = Field(description="剧本内容")


class ScriptCreate(ScriptBase):
    """创建剧本请求模型。"""

    pass


class ScriptUploadResponse(BaseResponse):
    """剧本上传响应模型。"""

    script_id: Optional[UUID] = None
    title: Optional[str] = None


class ScriptResponse(ScriptBase):
    """剧本响应模型。"""

    id: UUID
    parsed_structure: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    characters: List[CharacterResponse] = []
    episodes: List[EpisodeResponse] = []

    class Config:
        from_attributes = True


class ScriptParseRequest(BaseModel):
    """解析剧本请求模型。"""

    content: Optional[str] = Field(default=None, description="要解析的剧本文本，为空则使用剧本原有内容")


class ScriptParseResponse(BaseResponse):
    """解析剧本响应模型。"""

    script_id: UUID
    title: Optional[str] = None
    characters: List[CharacterResponse] = []
    episodes: List[EpisodeResponse] = []


# ==================== 演绎步骤相关 ====================

class PerformanceStepBase(BaseModel):
    """演绎步骤基础模型。"""

    step_number: int = Field(description="步骤序号")
    action: str = Field(description="动作指令")
    line: str = Field(description="DM台词")
    timing: Optional[str] = Field(default=None, description="节奏控制")
    music: Optional[str] = Field(default=None, description="背景音乐提示")


class PerformanceStepCreate(PerformanceStepBase):
    """创建演绎步骤请求模型。"""

    pass


class PerformanceStepResponse(PerformanceStepBase):
    """演绎步骤响应模型。"""

    id: UUID
    performance_plan_id: UUID

    class Config:
        from_attributes = True


# ==================== 演绎方案相关 ====================

class PerformancePlanBase(BaseModel):
    """演绎方案基础模型。"""

    episode_id: UUID = Field(description="环节ID")
    emotion_type: str = Field(description="情感类型")
    episode_type: str = Field(description="环节类型")
    scene: str = Field(description="具体场景")


class PerformancePlanCreate(PerformancePlanBase):
    """创建演绎方案请求模型。"""

    title: str = Field(description="演绎方案标题")
    duration: str = Field(default="5-8分钟", description="预计时长")
    props: Optional[str] = Field(default=None, description="道具清单")
    notes: Optional[str] = Field(default=None, description="注意事项")
    steps: List[PerformanceStepCreate] = Field(default=[], description="演绎步骤列表")


class PerformancePlanGenerateRequest(BaseModel):
    """生成演绎方案请求模型。"""

    episode_id: UUID = Field(description="环节ID")
    emotion_type: str = Field(description="情感类型：爱情/亲情/友情/家国")
    episode_type: str = Field(description="环节类型：心建/羁绊仪式/情感爆发")
    scene: str = Field(description="具体场景")


class PerformancePlanCollaborateRequest(PerformancePlanGenerateRequest):
    """协作模式生成演绎方案请求模型。"""

    user_idea: str = Field(description="DM提供的原始想法")


class PerformancePlanResponse(BaseModel):
    """演绎方案响应模型。"""

    id: UUID
    episode_id: UUID
    emotion_type: str
    episode_type: str
    scene: str
    title: str
    duration: str
    props: Optional[str] = None
    notes: Optional[str] = None
    is_collaborative: bool
    user_idea: Optional[str] = None
    ai_plan: Optional[str] = None
    comparison: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    steps: List[PerformanceStepResponse] = []

    class Config:
        from_attributes = True


class PerformanceComparisonResponse(BaseModel):
    """双轨对比响应模型。"""

    ai_plan: PerformancePlanResponse = Field(description="AI自动生成的方案")
    user_plan: PerformancePlanResponse = Field(description="基于用户想法的方案")
    comparison: dict = Field(description="对比分析")


class PerformancePlanListResponse(BaseModel):
    """演绎方案列表响应模型。"""

    plans: List[PerformancePlanResponse]
