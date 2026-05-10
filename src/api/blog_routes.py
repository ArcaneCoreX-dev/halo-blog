"""Public blog API routes.

Copyright (c) 2026 ArcaneCoreX-dev - MIT License
See LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.adapters.database import get_db
from src.config import settings
from src.domain.models import Category, Comment, Link, Post, Tag
from src.domain.schemas import CommentCreate, CommentOut
from src.services import comment_service, post_service

router = APIRouter(prefix="/api", tags=["blog"])


@router.get("/posts", summary="获取文章列表", description="分页获取已发布的文章，支持按分类、标签、关键词筛选。")
async def list_posts(
    page: int = 1,
    page_size: int = 10,
    category: str | None = None,
    tag: str | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    posts, total = await post_service.get_posts(
        db, page=page, page_size=page_size, status="published",
        category_slug=category, tag_slug=tag, keyword=q,
    )
    items = []
    for p in posts:
        items.append({
            "id": p.id, "title": p.title, "slug": p.slug,
            "summary": p.summary, "cover_image": p.cover_image,
            "views": p.views, "is_top": p.is_top,
            "category": {"id": p.category.id, "name": p.category.name, "slug": p.category.slug} if p.category else None,
            "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in p.tags],
            "published_at": p.published_at.isoformat() if p.published_at else None,
            "comment_count": len([c for c in p.comments if c.is_approved]),
        })
    total_pages = (total + page_size - 1) // page_size
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/posts/{slug}", summary="获取文章详情", description="根据 slug 获取单篇文章详情，自动增加浏览计数。")
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    post = await post_service.get_post_by_slug(db, slug)
    if not post or post.status != "published":
        raise HTTPException(status_code=404, detail="Post not found")
    await post_service.increment_views(db, post.id)
    return {
        "id": post.id, "title": post.title, "slug": post.slug,
        "summary": post.summary, "content": post.content, "content_html": post.content_html,
        "cover_image": post.cover_image, "views": post.views + 1, "is_top": post.is_top,
        "category": {"id": post.category.id, "name": post.category.name, "slug": post.category.slug} if post.category else None,
        "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in post.tags],
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "is_allow_comment": post.is_allow_comment,
        "comment_count": len([c for c in post.comments if c.is_approved]),
    }


@router.get("/posts/{post_id}/comments")
async def get_comments(post_id: int, db: AsyncSession = Depends(get_db)):
    comments = await comment_service.get_comments_by_post(db, post_id, approved_only=True)
    return [_serialize_comment(c) for c in comments]


@router.post("/comments", summary="提交评论", description="为文章提交评论，评论默认需要管理员审核后才会显示。")
async def add_comment(data: CommentCreate, request: Request, db: AsyncSession = Depends(get_db)):
    post = await post_service.get_post_by_id(db, data.post_id)
    if not post or post.status != "published":
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.is_allow_comment:
        raise HTTPException(status_code=403, detail="Comments are disabled")

    ip = request.client.host if request.client else ""
    comment = await comment_service.create_comment(db, data, ip=ip)
    return {"id": comment.id, "message": "Comment submitted, waiting for approval."}


@router.get("/categories", summary="获取分类列表", description="获取所有分类及其文章计数。")
async def list_categories(db: AsyncSession = Depends(get_db)):
    cats = (await db.execute(
        select(Category).order_by(Category.name)
    )).scalars().all()
    result = []
    for c in cats:
        count = (await db.execute(
            select(func.count()).select_from(Post).where(Post.category_id == c.id, Post.status == "published")
        )).scalar() or 0
        result.append({"id": c.id, "name": c.name, "slug": c.slug, "description": c.description, "post_count": count})
    return result


@router.get("/tags", summary="获取标签列表", description="获取所有标签及其文章计数。")
async def list_tags(db: AsyncSession = Depends(get_db)):
    tags = (await db.execute(select(Tag).order_by(Tag.name))).scalars().all()
    result = []
    for t in tags:
        count = (await db.execute(
            select(func.count()).select_from(Post).where(Post.tags.any(Tag.id == t.id), Post.status == "published")
        )).scalar() or 0
        result.append({"id": t.id, "name": t.name, "slug": t.slug, "post_count": count})
    return result


@router.get("/links")
async def list_links(db: AsyncSession = Depends(get_db)):
    links = (await db.execute(
        select(Link).where(Link.is_visible.is_(True)).order_by(Link.sort_order)
    )).scalars().all()
    return [{"id": l.id, "name": l.name, "url": l.url, "description": l.description} for l in links]


@router.get("/archives", summary="获取归档", description="获取所有已发布文章，按年月分组。")
async def archives(db: AsyncSession = Depends(get_db)):
    posts = (await db.execute(
        select(Post).where(Post.status == "published").order_by(Post.published_at.desc())
    )).scalars().all()
    grouped: dict[str, list] = {}
    for p in posts:
        if p.published_at:
            key = p.published_at.strftime("%Y-%m")
            if key not in grouped:
                grouped[key] = []
            grouped[key].append({
                "id": p.id, "title": p.title, "slug": p.slug,
                "published_at": p.published_at.isoformat(),
            })
    return grouped


def _serialize_comment(c: Comment) -> dict:
    return {
        "id": c.id, "post_id": c.post_id, "parent_id": c.parent_id,
        "author_name": c.author_name, "author_website": c.author_website,
        "content": c.content, "created_at": c.created_at.isoformat(),
        "replies": [_serialize_comment(r) for r in c.replies if r.is_approved],
    }
