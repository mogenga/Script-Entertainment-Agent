"""剧本管理API路由。"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models import Character, Episode, Script
from app.schemas import (
    EpisodeListResponse,
    EpisodeResponse,
    ScriptCreate,
    ScriptParseRequest,
    ScriptParseResponse,
    ScriptResponse,
    ScriptUploadResponse,
)

router = APIRouter(prefix="/scripts", tags=["剧本管理"])


@router.post(
    "",
    response_model=ScriptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建剧本",
)
async def create_script(
    data: ScriptCreate,
    session: AsyncSession = Depends(get_session),
) -> Script:
    """
    创建新剧本。

    - **title**: 剧本标题
    - **content**: 剧本内容文本
    """
    script = Script(title=data.title, content=data.content)
    session.add(script)
    await session.commit()
    await session.refresh(script)
    return script


@router.post(
    "/upload",
    response_model=ScriptUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="上传剧本文件",
)
async def upload_script(
    file: UploadFile = File(..., description="剧本文件（txt或docx格式）"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    上传剧本文件并创建剧本。

    支持 .txt 和 .docx 格式文件。
    """
    # 读取文件内容
    content = await file.read()

    try:
        if file.filename.endswith(".txt"):
            text_content = content.decode("utf-8")
        elif file.filename.endswith(".docx"):
            # TODO: 使用python-docx库解析docx文件
            # 暂时返回错误，提示只支持txt
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="docx格式暂时不支持，请使用txt格式",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件格式，请上传.txt或.docx文件",
            )
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件编码错误，请使用UTF-8编码的文本文件",
        )

    # 使用文件名（不含扩展名）作为标题
    title = file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename

    # 创建剧本
    script = Script(title=title, content=text_content)
    session.add(script)
    await session.commit()
    await session.refresh(script)

    return {
        "success": True,
        "message": "剧本上传成功",
        "script_id": script.id,
        "title": script.title,
    }


@router.get(
    "/{script_id}",
    response_model=ScriptResponse,
    summary="获取剧本详情",
)
async def get_script(
    script_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Script:
    """
    获取指定ID的剧本详情，包括角色和环节列表。
    """
    result = await session.execute(
        select(Script)
        .where(Script.id == script_id)
    )
    script = result.scalar_one_or_none()

    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"剧本不存在: {script_id}",
        )

    return script


@router.post(
    "/{script_id}/parse",
    response_model=ScriptParseResponse,
    summary="解析剧本结构",
)
async def parse_script(
    script_id: UUID,
    data: ScriptParseRequest | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    解析剧本结构，提取标题、角色列表和环节列表。

    - 如果提供了content，则解析提供的文本
    - 否则解析剧本原有内容
    - 解析结果会保存到数据库

    **TODO**: 当前为占位实现，实际解析逻辑需要接入ScriptParser Agent
    """
    # 获取剧本
    result = await session.execute(select(Script).where(Script.id == script_id))
    script = result.scalar_one_or_none()

    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"剧本不存在: {script_id}",
        )

    # 使用提供的文本或剧本原有内容
    content = data.content if data and data.content else script.content

    # TODO: 接入ScriptParser Agent进行实际解析
    # 当前返回模拟数据作为占位

    # 创建示例角色
    character_names = ["角色A", "角色B", "角色C"]
    characters = []
    for name in character_names:
        char = Character(
            script_id=script_id,
            name=name,
            description=f"{name}的描述",
        )
        session.add(char)
        characters.append(char)

    # 创建示环节
    episode_names = ["序幕", "第一幕", "第二幕", "终幕"]
    episodes = []
    for i, name in enumerate(episode_names):
        episode = Episode(
            script_id=script_id,
            name=name,
            content=f"{name}的内容...",
            episode_type="narrative",
            position=i,
        )
        session.add(episode)
        episodes.append(episode)

    await session.commit()

    # 刷新对象以获取ID
    for char in characters:
        await session.refresh(char)
    for ep in episodes:
        await session.refresh(ep)

    # 更新剧本解析状态
    script.parsed_structure = "{\"parsed\": true, \"character_count\": 3, \"episode_count\": 4}"
    await session.commit()

    return {
        "success": True,
        "message": "剧本解析完成（当前为模拟数据）",
        "script_id": script_id,
        "title": script.title,
        "characters": characters,
        "episodes": episodes,
    }


@router.get(
    "/{script_id}/episodes",
    response_model=EpisodeListResponse,
    summary="获取剧本环节列表",
)
async def get_script_episodes(
    script_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    获取指定剧本的所有环节列表，按位置排序。
    """
    # 检查剧本是否存在
    result = await session.execute(select(Script).where(Script.id == script_id))
    script = result.scalar_one_or_none()

    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"剧本不存在: {script_id}",
        )

    # 获取环节列表
    result = await session.execute(
        select(Episode)
        .where(Episode.script_id == script_id)
        .order_by(Episode.position)
    )
    episodes = result.scalars().all()

    return {"episodes": list(episodes)}
