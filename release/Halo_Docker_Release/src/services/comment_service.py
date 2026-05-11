"""Comment service.

Copyright (c) 2026 ArcaneCoreX-dev - MIT License
See LICENSE file for details.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.models import Comment
from src.domain.schemas import CommentCreate


async def get_comments_by_post(
    db: AsyncSession, post_id: int, approved_only: bool = True
) -> list[Comment]:
    """Get top-level comments with nested replies."""
    query = (
        select(Comment)
        .options(selectinload(Comment.replies))
        .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
    )
    if approved_only:
        query = query.where(Comment.is_approved.is_(True))
    query = query.order_by(Comment.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def get_all_comments(
    db: AsyncSession, page: int = 1, page_size: int = 20
) -> tuple[list[Comment], int]:
    """Admin: get all comments with pagination."""
    from sqlalchemy import func

    count_q = select(func.count()).select_from(Comment)
    total = (await db.execute(count_q)).scalar() or 0

    query = (
        select(Comment)
        .options(selectinload(Comment.replies))
        .where(Comment.parent_id.is_(None))
        .order_by(Comment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    return list(result.scalars().unique().all()), total


async def create_comment(db: AsyncSession, data: CommentCreate, ip: str = "") -> Comment:
    comment = Comment(
        post_id=data.post_id,
        parent_id=data.parent_id,
        author_name=data.author_name,
        author_email=data.author_email,
        author_website=data.author_website,
        content=data.content,
        ip_address=ip,
        is_approved=False,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def approve_comment(db: AsyncSession, comment_id: int) -> bool:
    comment = await db.get(Comment, comment_id)
    if not comment:
        return False
    comment.is_approved = True
    await db.commit()
    return True


async def delete_comment(db: AsyncSession, comment_id: int) -> bool:
    comment = await db.get(Comment, comment_id)
    if not comment:
        return False
    await db.delete(comment)
    await db.commit()
    return True


async def get_pending_count(db: AsyncSession) -> int:
    from sqlalchemy import func

    q = select(func.count()).select_from(Comment).where(Comment.is_approved.is_(False))
    return (await db.execute(q)).scalar() or 0
