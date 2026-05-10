"""Pydantic schemas for request/response validation.

Copyright (c) 2026 ArcaneCoreX-dev - MIT License
See LICENSE file for details.
"""

from datetime import datetime

from pydantic import BaseModel, Field


# --- Category ---
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str = ""


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    created_at: datetime
    post_count: int = 0

    model_config = {"from_attributes": True}


# --- Tag ---
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)


class TagOut(BaseModel):
    id: int
    name: str
    slug: str
    post_count: int = 0

    model_config = {"from_attributes": True}


# --- Post ---
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    summary: str = ""
    content: str = ""
    cover_image: str = ""
    status: str = "draft"
    is_top: bool = False
    is_allow_comment: bool = True
    category_id: int | None = None
    tag_ids: list[int] = []


class PostUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    summary: str | None = None
    content: str | None = None
    cover_image: str | None = None
    status: str | None = None
    is_top: bool | None = None
    is_allow_comment: bool | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None


class PostOut(BaseModel):
    id: int
    title: str
    slug: str
    summary: str
    content: str
    content_html: str
    cover_image: str
    status: str
    is_top: bool
    is_allow_comment: bool
    views: int
    category_id: int | None
    category: CategoryOut | None = None
    tags: list[TagOut] = []
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None
    comment_count: int = 0

    model_config = {"from_attributes": True}


class PostListItem(BaseModel):
    id: int
    title: str
    slug: str
    summary: str
    cover_image: str
    status: str
    is_top: bool
    views: int
    category: CategoryOut | None = None
    tags: list[TagOut] = []
    created_at: datetime
    published_at: datetime | None
    comment_count: int = 0

    model_config = {"from_attributes": True}


# --- Comment ---
class CommentCreate(BaseModel):
    post_id: int
    parent_id: int | None = None
    author_name: str = Field(..., min_length=1, max_length=50)
    author_email: str = ""
    author_website: str = ""
    content: str = Field(..., min_length=1, max_length=2000)


class CommentOut(BaseModel):
    id: int
    post_id: int
    parent_id: int | None
    author_name: str
    author_website: str
    content: str
    is_approved: bool
    created_at: datetime
    replies: list["CommentOut"] = []

    model_config = {"from_attributes": True}


# --- Link ---
class LinkCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    sort_order: int = 0
    is_visible: bool = True


class LinkOut(BaseModel):
    id: int
    name: str
    url: str
    description: str
    sort_order: int
    is_visible: bool

    model_config = {"from_attributes": True}


# --- User ---
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Pagination ---
class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
