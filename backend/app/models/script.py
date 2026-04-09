"""剧本相关数据模型，包含剧本、角色和环节。"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.performance import PerformancePlan


class CharacterRelationship(SQLModel, table=True):
    """角色关系关联表，表示两个角色之间的关系。"""

    __tablename__ = "character_relationships"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: UUID = Field(foreign_key="characters.id", index=True)
    target_id: UUID = Field(foreign_key="characters.id", index=True)
    relationship_type: str = Field(description="关系类型，如爱情/亲情/友情/家国")
    description: Optional[str] = Field(default=None, description="关系描述")


class Character(SQLModel, table=True):
    """角色模型，表示剧本中的一个角色。"""

    __tablename__ = "characters"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    script_id: UUID = Field(foreign_key="scripts.id", index=True)
    name: str = Field(description="角色名称")
    description: Optional[str] = Field(default=None, description="角色描述")
    background: Optional[str] = Field(default=None, description="角色背景故事")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关联关系
    script: "Script" = Relationship(back_populates="characters")
    relationships: List["CharacterRelationship"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[CharacterRelationship.source_id]"}
    )


class Episode(SQLModel, table=True):
    """环节模型，表示剧本中的一个环节或片段。"""

    __tablename__ = "episodes"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    script_id: UUID = Field(foreign_key="scripts.id", index=True)
    name: str = Field(description="环节名称")
    content: str = Field(description="环节内容文本")
    episode_type: str = Field(description="环节类型：narrative/interaction/clue/emotion")
    position: int = Field(default=0, description="环节在剧本中的顺序位置")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关联关系
    script: "Script" = Relationship(back_populates="episodes")
    performance_plans: List["PerformancePlan"] = Relationship(back_populates="episode")


class Script(SQLModel, table=True):
    """剧本模型，表示一个完整的剧本。"""

    __tablename__ = "scripts"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    title: str = Field(description="剧本标题")
    content: str = Field(description="原始剧本内容")
    parsed_structure: Optional[str] = Field(
        default=None, description="解析后的结构化数据（JSON字符串）"
    )

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关联关系
    characters: List["Character"] = Relationship(back_populates="script")
    episodes: List["Episode"] = Relationship(back_populates="script")
