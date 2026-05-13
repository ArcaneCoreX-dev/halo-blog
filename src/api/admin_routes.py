"""Admin API routes — CRUD for posts, categories, tags, comments, settings.

Copyright (c) 2026 ArcaneCoreX-dev - MIT License
See LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.adapters.database import get_db
from src.domain.models import Category, Comment, Link, Post, Setting, Tag, User
from src.domain.schemas import (
    CategoryCreate,
    CategoryOut,
    CommentOut,
    LinkCreate,
    LinkOut,
    LoginRequest,
    TokenOut,
    PostCreate,
    PostListItem,
    PostOut,
    PostUpdate,
    TagCreate,
    TagOut,
)
from src.services import auth, comment_service, post_service

router = APIRouter(prefix="/admin/api", tags=["admin"])


# ── Auth ─────────────────────────────────────────────
@router.post(
    "/login",
    response_model=TokenOut,
    summary="管理员登录",
    description="使用用户名和密码登录，返回 JWT Token。",
)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (
        await db.execute(select(User).where(User.username == data.username))
    ).scalar_one_or_none()
    if not user or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.username})
    return TokenOut(access_token=token)


@router.get("/me")
async def get_me(current_user: User = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "role": current_user.role,
    }


# ── Dashboard ────────────────────────────────────────
@router.get("/dashboard", summary="仪表盘数据", description="获取博客统计数据和最近文章/评论。")
async def dashboard(db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)):
    post_count = (await db.execute(select(func.count()).select_from(Post))).scalar() or 0
    published_count = (
        await db.execute(select(func.count()).select_from(Post).where(Post.status == "published"))
    ).scalar() or 0
    comment_count = (await db.execute(select(func.count()).select_from(Comment))).scalar() or 0
    pending_comments = await comment_service.get_pending_count(db)
    category_count = (await db.execute(select(func.count()).select_from(Category))).scalar() or 0
    tag_count = (await db.execute(select(func.count()).select_from(Tag))).scalar() or 0

    recent_posts = (
        (await db.execute(select(Post).order_by(Post.created_at.desc()).limit(5))).scalars().all()
    )

    recent_comments = (
        (await db.execute(select(Comment).order_by(Comment.created_at.desc()).limit(5)))
        .scalars()
        .all()
    )

    return {
        "stats": {
            "posts": post_count,
            "published": published_count,
            "comments": comment_count,
            "pending_comments": pending_comments,
            "categories": category_count,
            "tags": tag_count,
        },
        "recent_posts": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
            }
            for p in recent_posts
        ],
        "recent_comments": [
            {
                "id": c.id,
                "author_name": c.author_name,
                "content": c.content[:50],
                "is_approved": c.is_approved,
                "created_at": c.created_at.isoformat(),
            }
            for c in recent_comments
        ],
    }


# ── Posts CRUD ───────────────────────────────────────
@router.get("/posts")
async def admin_list_posts(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(auth.get_current_user),
):
    posts, total = await post_service.get_posts(
        db, page=page, page_size=page_size, status=status, keyword=q
    )
    items = []
    for p in posts:
        items.append(
            {
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "status": p.status,
                "views": p.views,
                "is_top": p.is_top,
                "category": {"id": p.category.id, "name": p.category.name} if p.category else None,
                "tags": [{"id": t.id, "name": t.name} for t in p.tags],
                "created_at": p.created_at.isoformat(),
                "published_at": p.published_at.isoformat() if p.published_at else None,
                "comment_count": len(p.comments),
            }
        )
    total_pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.post("/posts")
async def admin_create_post(
    data: PostCreate, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    post = await post_service.create_post(db, data)
    return {"id": post.id, "slug": post.slug}


@router.get("/posts/{post_id}")
async def admin_get_post(
    post_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    post = await post_service.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "summary": post.summary,
        "content": post.content,
        "content_html": post.content_html,
        "cover_image": post.cover_image,
        "status": post.status,
        "is_top": post.is_top,
        "is_allow_comment": post.is_allow_comment,
        "views": post.views,
        "category_id": post.category_id,
        "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in post.tags],
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
        "published_at": post.published_at.isoformat() if post.published_at else None,
    }


@router.put("/posts/{post_id}")
async def admin_update_post(
    post_id: int,
    data: PostUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(auth.get_current_user),
):
    post = await post_service.update_post(db, post_id, data)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": post.id, "slug": post.slug}


@router.delete("/posts/{post_id}")
async def admin_delete_post(
    post_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    ok = await post_service.delete_post(db, post_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Deleted"}


# ── Categories CRUD ──────────────────────────────────
@router.get("/categories")
async def admin_list_categories(
    db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    cats = (await db.execute(select(Category).order_by(Category.name))).scalars().all()
    result = []
    for c in cats:
        count = (
            await db.execute(select(func.count()).select_from(Post).where(Post.category_id == c.id))
        ).scalar() or 0
        result.append(
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "description": c.description,
                "post_count": count,
            }
        )
    return result


@router.post("/categories")
async def admin_create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(auth.get_current_user),
):
    cat = Category(name=data.name, slug=data.slug, description=data.description)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return {"id": cat.id, "name": cat.name, "slug": cat.slug}


@router.put("/categories/{cat_id}")
async def admin_update_category(
    cat_id: int,
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(auth.get_current_user),
):
    cat = await db.get(Category, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.name = data.name
    cat.slug = data.slug
    cat.description = data.description
    await db.commit()
    return {"id": cat.id}


@router.delete("/categories/{cat_id}")
async def admin_delete_category(
    cat_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    cat = await db.get(Category, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(cat)
    await db.commit()
    return {"message": "Deleted"}


# ── Tags CRUD ────────────────────────────────────────
@router.get("/tags")
async def admin_list_tags(
    db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    tags = (await db.execute(select(Tag).order_by(Tag.name))).scalars().all()
    return [{"id": t.id, "name": t.name, "slug": t.slug} for t in tags]


@router.post("/tags")
async def admin_create_tag(
    data: TagCreate, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    tag = Tag(name=data.name, slug=data.slug)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return {"id": tag.id}


@router.delete("/tags/{tag_id}")
async def admin_delete_tag(
    tag_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(tag)
    await db.commit()
    return {"message": "Deleted"}


# ── Comments Admin ───────────────────────────────────
@router.get("/comments")
async def admin_list_comments(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(auth.get_current_user),
):
    comments, total = await comment_service.get_all_comments(db, page=page, page_size=page_size)
    items = []
    for c in comments:
        items.append(
            {
                "id": c.id,
                "post_id": c.post_id,
                "author_name": c.author_name,
                "author_email": c.author_email,
                "content": c.content,
                "is_approved": c.is_approved,
                "created_at": c.created_at.isoformat(),
                "reply_count": len(c.replies) if c.replies else 0,
            }
        )
    total_pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.put("/comments/{comment_id}/approve")
async def admin_approve_comment(
    comment_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    ok = await comment_service.approve_comment(db, comment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Approved"}


@router.delete("/comments/{comment_id}")
async def admin_delete_comment(
    comment_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    ok = await comment_service.delete_comment(db, comment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Deleted"}


# ── Links CRUD ───────────────────────────────────────
@router.get("/links")
async def admin_list_links(
    db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    links = (await db.execute(select(Link).order_by(Link.sort_order))).scalars().all()
    return [
        {
            "id": l.id,
            "name": l.name,
            "url": l.url,
            "description": l.description,
            "sort_order": l.sort_order,
            "is_visible": l.is_visible,
        }
        for l in links
    ]


@router.post("/links")
async def admin_create_link(
    data: LinkCreate, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    link = Link(
        name=data.name,
        url=data.url,
        description=data.description,
        sort_order=data.sort_order,
        is_visible=data.is_visible,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return {"id": link.id}


@router.delete("/links/{link_id}")
async def admin_delete_link(
    link_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    link = await db.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    await db.delete(link)
    await db.commit()
    return {"message": "Deleted"}


# ── Settings ─────────────────────────────────────────
@router.get("/settings")
async def admin_get_settings(
    db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    settings = (await db.execute(select(Setting))).scalars().all()
    return {s.key: s.value for s in settings}


@router.put("/settings")
async def admin_update_settings(
    data: dict, db: AsyncSession = Depends(get_db), _: User = Depends(auth.get_current_user)
):
    for key, value in data.items():
        existing = (
            await db.execute(select(Setting).where(Setting.key == key))
        ).scalar_one_or_none()
        if existing:
            existing.value = str(value)
        else:
            db.add(Setting(key=key, value=str(value)))
    await db.commit()
    return {"message": "Settings updated"}


# ── Profile ──────────────────────────────────────────
@router.get("/profile")
async def admin_get_profile(current_user: User = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "email": current_user.email,
        "avatar": current_user.avatar,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat(),
    }


@router.put("/profile")
async def admin_update_profile(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    if "display_name" in data:
        current_user.display_name = data["display_name"]
    if "email" in data:
        current_user.email = data["email"]
    if "avatar" in data:
        current_user.avatar = data["avatar"]
    await db.commit()
    return {"message": "Profile updated"}


@router.put("/profile/password")
async def admin_change_password(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Old and new passwords are required")
    if not auth.verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    current_user.password_hash = auth.hash_password(new_password)
    await db.commit()
    return {"message": "Password changed"}



# ── Export single post as Markdown ──────────────────────────
@router.get("/posts/{post_id}/export-markdown", summary="导出单篇文章为 Markdown",
            description="导出单篇文章为 Markdown 文件，带图片 assets 文件夹。")
async def export_single_post_markdown(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(auth.get_current_user),
):
    import zipfile
    import io
    import urllib.parse
    from fastapi.responses import StreamingResponse
    import re as re_export

    result = await db.execute(select(Post).where(Post.id == post_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")

    zip_buffer = io.BytesIO()
    slug = p.slug or f'post-{p.id}'

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Write the markdown file at root of zip
        # Extract image URLs from content
        markdown_content = f"# {p.title}\n\n{p.content or ''}"
        zf.writestr(f"{slug}.md", markdown_content)

        # Find all image references in content
        image_urls = set()
        if p.content:
            # Markdown images: ![alt](/path) or ![alt](url)
            for m in re_export.finditer(r'!\[.*?\]\((.*?)\)', p.content):
                image_urls.add(m.group(1))
            # HTML img tags
            for m in re_export.finditer(r'<img[^>]+src=["\'](.*?)["\']', p.content):
                image_urls.add(m.group(1))
            # Direct image links on their own line
            for m in re_export.finditer(r'(?<![\[!])(https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp|svg|bmp))', p.content, re_export.IGNORECASE):
                image_urls.add(m.group(1))

        if image_urls:
            import urllib.request
            import os as os_mod

            for url in image_urls:
                # Skip data URIs and local relative paths
                if url.startswith('data:') or url.startswith('{{'):
                    continue
                try:
                    # Determine a filename
                    url_path = url.split('?')[0]
                    basename = url_path.rstrip('/').split('/')[-1] or 'image.png'
                    # Put in assets folder
                    assets_path = f"assets/{basename}"
                    # Only add if not already included
                    if assets_path not in [zi.filename for zi in zf.filelist]:
                        req = urllib.request.Request(url, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            img_data = resp.read()
                        zf.writestr(assets_path, img_data)
                except Exception:
                    pass  # Skip images that fail to download

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(slug)}.zip"}
    )


# ── Import Markdown ──────────────────────────────────────────
@router.post("/import-markdown", summary="导入 Markdown 文件",
             description="上传 .md 文件批量导入文章。")
async def import_markdown(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(auth.get_current_user),
):
    import markdown as md_lib
    import re as re_import

    form = await request.form()
    files = form.getlist("files")

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    imported = 0
    for file in files:
        content_bytes = await file.read()
        text = content_bytes.decode("utf-8", errors="replace")

        # Extract title from first H1 or filename
        title_match = re_import.search(r"^#\s+(.+)$", text, re_import.MULTILINE)
        title = title_match.group(1).strip() if title_match else file.filename.replace(".md", "")

        # Generate slug from title
        slug = re_import.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", title.lower()).strip("-")

        # Extract summary (first non-empty, non-header paragraph)
        summary = ""
        for line in text.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("!["):
                summary = line[:200]
                break

        content_html = md_lib.markdown(text, extensions=["fenced_code", "tables", "codehilite", "toc"])
        now = datetime.utcnow()
        post = Post(
            title=title,
            slug=slug,
            content=text,
            content_html=content_html,
            summary=summary,
            status="published",
            published_at=now,
            is_allow_comment=True,
        )
        db.add(post)
        imported += 1

    await db.commit()
    return {"message": f"Imported {imported} Markdown files", "count": imported}
