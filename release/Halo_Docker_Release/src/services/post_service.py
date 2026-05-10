"""Post CRUD service.

Copyright (c) 2026 ArcaneCoreX-dev - MIT License
See LICENSE file for details.
"""

from datetime import datetime

import markdown
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.models import Category, Post, Tag
from src.domain.schemas import PostCreate, PostUpdate


async def get_posts(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    status: str | None = None,
    category_slug: str | None = None,
    tag_slug: str | None = None,
    keyword: str | None = None,
) -> tuple[list[Post], int]:
    """Get paginated posts with optional filters."""
    query = select(Post).options(
        selectinload(Post.category),
        selectinload(Post.tags),
        selectinload(Post.comments),
    )

    if status:
        query = query.where(Post.status == status)
    if category_slug:
        query = query.join(Category).where(Category.slug == category_slug)
    if tag_slug:
        query = query.join(Post.tags).where(Tag.slug == tag_slug)
    if keyword:
        query = query.where(
            Post.title.contains(keyword) | Post.summary.contains(keyword)
        )

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginate
    query = query.order_by(Post.is_top.desc(), Post.published_at.desc().nullslast(), Post.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    posts = list(result.scalars().unique().all())

    return posts, total


async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    """Get single post by slug with relations."""
    query = (
        select(Post)
        .options(selectinload(Post.category), selectinload(Post.tags), selectinload(Post.comments))
        .where(Post.slug == slug)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
    query = (
        select(Post)
        .options(selectinload(Post.category), selectinload(Post.tags), selectinload(Post.comments))
        .where(Post.id == post_id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_post(db: AsyncSession, data: PostCreate) -> Post:
    """Create a new post."""
    content_html = markdown.markdown(
        data.content, extensions=["fenced_code", "tables", "codehilite", "toc"]
    )
    now = datetime.utcnow()

    post = Post(
        title=data.title,
        slug=data.slug,
        summary=data.summary,
        content=data.content,
        content_html=content_html,
        cover_image=data.cover_image,
        status=data.status,
        is_top=data.is_top,
        is_allow_comment=data.is_allow_comment,
        category_id=data.category_id,
        published_at=now if data.status == "published" else None,
    )

    # Attach tags
    if data.tag_ids:
        tags = (await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))).scalars().all()
        post.tags = list(tags)

    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def update_post(db: AsyncSession, post_id: int, data: PostUpdate) -> Post | None:
    """Update an existing post."""
    post = await get_post_by_id(db, post_id)
    if not post:
        return None

    update_data = data.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    for field, value in update_data.items():
        if field == "content" and value is not None:
            post.content = value
            post.content_html = markdown.markdown(
                value, extensions=["fenced_code", "tables", "codehilite", "toc"]
            )
        elif field == "status" and value == "published" and post.status != "published":
            setattr(post, field, value)
            post.published_at = datetime.utcnow()
        else:
            setattr(post, field, value)

    if tag_ids is not None:
        tags = (await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))).scalars().all()
        post.tags = list(tags)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(db: AsyncSession, post_id: int) -> bool:
    post = await get_post_by_id(db, post_id)
    if not post:
        return False
    await db.delete(post)
    await db.commit()
    return True


async def increment_views(db: AsyncSession, post_id: int) -> None:
    post = await db.get(Post, post_id)
    if post:
        post.views = (post.views or 0) + 1
        await db.commit()
