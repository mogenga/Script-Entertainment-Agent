"""演绎设计API路由。"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models import Episode, PerformancePlan, PerformanceStep
from app.schemas import (
    PerformanceComparisonResponse,
    PerformancePlanCollaborateRequest,
    PerformancePlanGenerateRequest,
    PerformancePlanResponse,
)

router = APIRouter(prefix="/performances", tags=["演绎设计"])


@router.post(
    "",
    response_model=PerformancePlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="自动生成演绎方案",
)
async def generate_performance(
    data: PerformancePlanGenerateRequest,
    session: AsyncSession = Depends(get_session),
) -> PerformancePlan:
    """
    为指定环节自动生成演绎方案。

    - **episode_id**: 目标环节ID
    - **emotion_type**: 情感类型（爱情/亲情/友情/家国）
    - **episode_type**: 环节类型（心建/羁绊仪式/情感爆发）
    - **scene**: 具体场景描述

    **TODO**: 当前为占位实现，实际生成逻辑需要接入Agent系统
    """
    # 检查环节是否存在
    result = await session.execute(
        select(Episode).where(Episode.id == data.episode_id)
    )
    episode = result.scalar_one_or_none()

    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"环节不存在: {data.episode_id}",
        )

    # TODO: 接入StrategyDesigner和PerformanceDesigner Agent
    # 当前返回模拟数据

    # 创建演绎方案
    plan = PerformancePlan(
        episode_id=data.episode_id,
        emotion_type=data.emotion_type,
        episode_type=data.episode_type,
        scene=data.scene,
        title=f"{data.scene}演绎方案",
        duration="5-8分钟",
        props='["道具1", "道具2"]',
        notes="注意事项示例",
        is_collaborative=False,
    )
    session.add(plan)
    await session.commit()
    await session.refresh(plan)

    # 创建演绎步骤
    steps_data = [
        {
            "step_number": 1,
            "action": "请玩家站起来，面对DM",
            "line": "现在，请闭上眼睛，想象你就在那个场景中...",
            "timing": "停顿3秒",
            "music": "轻柔背景音乐",
        },
        {
            "step_number": 2,
            "action": "DM递出道具",
            "line": "这是TA留给你的信物，现在我将它交到你手中...",
            "timing": None,
            "music": "情感音乐渐强",
        },
        {
            "step_number": 3,
            "action": "引导玩家进行互动",
            "line": "你愿意为TA做这个选择吗？",
            "timing": "等待玩家回应",
            "music": "音乐达到高潮",
        },
    ]

    for step_data in steps_data:
        step = PerformanceStep(
            performance_plan_id=plan.id,
            **step_data,
        )
        session.add(step)

    await session.commit()
    await session.refresh(plan)

    return plan


@router.post(
    "/collaborate",
    response_model=PerformanceComparisonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="协作模式生成演绎方案",
)
async def collaborate_performance(
    data: PerformancePlanCollaborateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    协作模式生成演绎方案，同时生成AI方案和用户想法方案，并提供对比分析。

    - **episode_id**: 目标环节ID
    - **emotion_type**: 情感类型
    - **episode_type**: 环节类型
    - **scene**: 具体场景
    - **user_idea**: DM提供的原始想法

    **TODO**: 当前为占位实现，实际生成逻辑需要接入Orchestrator Agent
    """
    # 检查环节是否存在
    result = await session.execute(
        select(Episode).where(Episode.id == data.episode_id)
    )
    episode = result.scalar_one_or_none()

    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"环节不存在: {data.episode_id}",
        )

    # TODO: 接入Orchestrator Agent实现双轨生成
    # 当前返回模拟数据

    # 创建AI方案
    ai_plan = PerformancePlan(
        episode_id=data.episode_id,
        emotion_type=data.emotion_type,
        episode_type=data.episode_type,
        scene=data.scene,
        title=f"AI方案：{data.scene}演绎",
        duration="5-8分钟",
        props='["AI推荐道具1", "AI推荐道具2"]',
        notes="AI方案注意事项",
        is_collaborative=True,
        ai_plan='{"approach": "AI生成的方案思路"}',
    )
    session.add(ai_plan)
    await session.commit()
    await session.refresh(ai_plan)

    # 创建AI方案的步骤
    for i in range(1, 4):
        step = PerformanceStep(
            performance_plan_id=ai_plan.id,
            step_number=i,
            action=f"AI步骤{i}动作",
            line=f"AI步骤{i}台词",
            timing=None,
            music=None,
        )
        session.add(step)

    # 创建用户方案
    user_plan = PerformancePlan(
        episode_id=data.episode_id,
        emotion_type=data.emotion_type,
        episode_type=data.episode_type,
        scene=data.scene,
        title=f"你的方案：{data.scene}演绎",
        duration="6-10分钟",
        props='["用户道具1", "用户道具2"]',
        notes="基于你的想法的方案",
        is_collaborative=True,
        user_idea=data.user_idea,
    )
    session.add(user_plan)
    await session.commit()
    await session.refresh(user_plan)

    # 创建用户方案的步骤
    for i in range(1, 4):
        step = PerformanceStep(
            performance_plan_id=user_plan.id,
            step_number=i,
            action=f"用户步骤{i}动作",
            line=f"用户步骤{i}台词",
            timing=None,
            music=None,
        )
        session.add(step)

    await session.commit()
    await session.refresh(ai_plan)
    await session.refresh(user_plan)

    # 对比分析
    comparison = {
        "ai_plan": {
            "strengths": ["结构化程度高", "节奏把控精准", "易于执行"],
            "suggestions": ["可增加更多情感细节"],
        },
        "user_plan": {
            "strengths": ["情感真挚", "有独特创意", "贴合剧本"],
            "suggestions": ["节奏可以更加紧凑"],
        },
        "recommendation": "建议结合AI的结构化方案和你的情感表达，创造更好的演绎效果。",
    }

    return {
        "ai_plan": ai_plan,
        "user_plan": user_plan,
        "comparison": comparison,
    }


@router.get(
    "/{plan_id}",
    response_model=PerformancePlanResponse,
    summary="获取演绎方案详情",
)
async def get_performance(
    plan_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> PerformancePlan:
    """
    获取指定ID的演绎方案详情，包括所有步骤。
    """
    result = await session.execute(
        select(PerformancePlan).where(PerformancePlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"演绎方案不存在: {plan_id}",
        )

    return plan
