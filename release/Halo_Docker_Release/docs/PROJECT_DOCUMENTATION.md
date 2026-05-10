# Halo Blog 项目文档

> **版本：** 0.1.0 | **技术栈：** Python 3.12 + FastAPI + SQLAlchemy + Jinja2 | **部署：** Docker

---

## 目录

1. [项目概述](#1-项目概述)
2. [后端文件结构详解](#2-后端文件结构详解)
3. [数据模型设计](#3-数据模型设计)
4. [API 接口文档](#4-api-接口文档)
5. [配置参数说明](#5-配置参数说明)
6. [Docker 部署指南](#6-docker-部署指南)
7. [前端模板系统](#7-前端模板系统)
8. [认证与安全](#8-认证与安全)
9. [常见修改指南](#9-常见修改指南)
10. [故障排查](#10-故障排查)

---

## 1. 项目概述

Halo Blog 是一个类似 [Halo](https://halo.run/) 的轻量级个人博客系统，使用 Python 全栈开发。

### 核心特性

- 📝 文章管理（Markdown 编辑器 + 实时预览）
- 📂 分类 / 🏷️ 标签系统
- 💬 评论系统（支持审核机制）
- 🔗 友情链接管理
- 📊 数据仪表盘
- 🔐 JWT 认证的管理后台
- 📱 响应式设计
- 🐳 Docker 一键部署

### 技术架构

```
┌─────────────────────────────────────────────┐
│              浏览器 (前端)                     │
│   Jinja2 SSR + 原生 JS SPA                   │
└──────────────────┬──────────────────────────┘
                   │ HTTP
┌──────────────────▼──────────────────────────┐
│           FastAPI 应用层                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ API 路由  │  │ 模板渲染  │  │ 静态文件  │   │
│  └────┬─────┘  └────┬─────┘  └──────────┘   │
│       │              │                        │
│  ┌────▼──────────────▼─────┐                 │
│  │      Service 层          │                 │
│  │  post_service            │                 │
│  │  comment_service         │                 │
│  │  auth (JWT)              │                 │
│  └────────────┬────────────┘                 │
│               │                               │
│  ┌────────────▼────────────┐                 │
│  │    Domain 层 (ORM)       │                 │
│  │  SQLAlchemy Models       │                 │
│  │  Pydantic Schemas        │                 │
│  └────────────┬────────────┘                 │
│               │                               │
│  ┌────────────▼────────────┐                 │
│  │    Adapter 层            │                 │
│  │  SQLite (aiosqlite)      │                 │
│  └─────────────────────────┘                 │
└──────────────────────────────────────────────┘
```

---

## 2. 后端文件结构详解

```
E:\Docker\Halo_Docker\
│
├── Dockerfile                    # Docker 镜像构建文件
├── docker-compose.yml            # 容器编排配置
├── pyproject.toml                # Python 项目依赖配置
├── .env.example                  # 环境变量模板
├── .dockerignore                 # Docker 构建排除文件
│
├── data/                         # 数据库文件（挂载卷）
│   └── blog.db                   # SQLite 数据库
│
├── uploads/                      # 上传文件目录（挂载卷）
│
└── src/                          # ===== 源代码目录 =====
    ├── __init__.py
    ├── main.py                   # 🚀 应用入口（FastAPI 实例 + 路由注册）
    ├── config.py                 # ⚙️ 配置管理（Pydantic Settings）
    │
    ├── domain/                   # 📦 领域层
    │   ├── __init__.py
    │   ├── models.py             # 数据模型（SQLAlchemy ORM）
    │   └── schemas.py            # API Schema（Pydantic 验证）
    │
    ├── adapters/                 # 🔌 适配器层
    │   ├── __init__.py
    │   └── database.py           # 数据库引擎 + 会话管理
    │
    ├── services/                 # 💼 业务逻辑层
    │   ├── __init__.py
    │   ├── post_service.py       # 文章 CRUD 服务
    │   ├── comment_service.py    # 评论服务
    │   └── auth.py               # JWT 认证 + 密码哈希
    │
    ├── api/                      # 🌐 API 路由层
    │   ├── __init__.py
    │   ├── blog_routes.py        # 前台公开 API（14 个接口）
    │   └── admin_routes.py       # 后台管理 API（25+ 个接口）
    │
    ├── templates/                # 📄 Jinja2 模板
    │   ├── theme/                # 前台主题模板
    │   │   ├── base.html         # 基础布局（Header + Footer）
    │   │   ├── index.html        # 首页（文章列表）
    │   │   ├── post.html         # 文章详情页
    │   │   ├── archives.html     # 归档页
    │   │   ├── categories.html   # 分类页
    │   │   └── links.html        # 友链页
    │   └── admin/
    │       └── dashboard.html    # 管理后台 SPA 入口
    │
    └── static/                   # 🎨 静态资源
        ├── css/
        │   ├── style.css         # 前台主样式（~300 行）
        │   └── admin.css         # 管理后台样式（~200 行）
        └── js/
            ├── app.js            # 前台公共脚本
            └── admin.js          # 管理后台 SPA 逻辑（~600 行）
```

### 各层职责说明

#### `config.py` — 配置中心

使用 `pydantic-settings` 管理所有配置，支持环境变量覆盖。

```python
class Settings(BaseSettings):
    app_name: str = "Halo Blog"        # 应用名称
    debug: bool = False                 # 调试模式
    secret_key: str = "change-me"       # JWT 密钥
    database_url: str = "sqlite+aiosqlite:///./data/blog.db"
    admin_username: str = "admin"       # 管理员用户名
    admin_password: str = "admin123"    # 管理员密码
    blog_title: str = "My Blog"         # 博客标题
    posts_per_page: int = 10            # 每页文章数
    max_upload_size: int = 10485760     # 上传大小限制 (10MB)

    model_config = {"env_prefix": "HALO_"}  # 环境变量前缀
```

**所有配置项都可通过 `HALO_` 前缀的环境变量覆盖。**

#### `domain/models.py` — 数据模型

定义 8 张数据库表，使用 SQLAlchemy 2.0 异步 ORM：

| 模型 | 表名 | 说明 |
|------|------|------|
| `Post` | `posts` | 文章主表 |
| `Category` | `categories` | 分类 |
| `Tag` | `tags` | 标签 |
| `PostTag` | `post_tags` | 文章-标签关联表 |
| `Comment` | `comments` | 评论（支持嵌套回复） |
| `User` | `users` | 用户（管理员） |
| `Link` | `links` | 友情链接 |
| `Setting` | `settings` | 系统设置（KV 存储） |

#### `domain/schemas.py` — 请求/响应模型

定义 Pydantic v2 Schema，用于 API 请求验证和响应序列化：

- `PostCreate` / `PostUpdate` — 文章创建/更新
- `CategoryCreate` / `TagCreate` — 分类/标签创建
- `CommentCreate` — 评论提交
- `LoginRequest` / `TokenOut` — 认证
- `PaginatedResponse` — 分页响应

#### `adapters/database.py` — 数据库连接

```python
engine = create_async_engine(settings.database_url)      # 异步引擎
async_session = async_sessionmaker(engine)               # 会话工厂

async def init_db():          # 建表（启动时调用）
async def get_db():           # FastAPI 依赖注入
```

#### `services/` — 业务逻辑

| 文件 | 职责 | 核心函数 |
|------|------|---------|
| `post_service.py` | 文章 CRUD | `get_posts()`, `create_post()`, `update_post()`, `delete_post()`, `increment_views()` |
| `comment_service.py` | 评论管理 | `get_comments_by_post()`, `create_comment()`, `approve_comment()`, `delete_comment()` |
| `auth.py` | 认证 | `hash_password()`, `verify_password()`, `create_access_token()`, `get_current_user()` |

#### `api/` — 路由定义

- `blog_routes.py` — 前台公开接口（无需认证）
- `admin_routes.py` — 后台管理接口（JWT 认证）

#### `main.py` — 应用入口

```python
app = FastAPI(lifespan=lifespan)       # 创建 FastAPI 实例
app.mount("/static", ...)              # 挂载静态文件
app.mount("/uploads", ...)             # 挂载上传文件
templates = Jinja2Templates(...)       # 初始化模板引擎
app.include_router(blog_router)        # 注册前台路由
app.include_router(admin_router)       # 注册后台路由
```

---

## 3. 数据模型设计

### ER 关系图

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Category │────<│   Post   │>────│   Tag    │
│          │     │          │     │          │
│ id       │     │ id       │     │ id       │
│ name     │     │ title    │     │ name     │
│ slug     │     │ slug     │     │ slug     │
│ desc     │     │ content  │     └──────────┘
└──────────┘     │ content_ │          │
                 │ html     │     ┌────┴────┐
                 │ status   │     │ PostTag │
                 │ views    │     │ post_id │
                 │ category_│     │ tag_id  │
                 │ id       │     └─────────┘
                 └────┬─────┘
                      │
            ┌─────────┼─────────┐
            │                   │
     ┌──────▼──────┐    ┌──────▼──────┐
     │   Comment   │    │    User     │
     │             │    │             │
     │ id          │    │ id          │
     │ post_id     │    │ username    │
     │ parent_id   │    │ password_   │
     │ author_name │    │ hash        │
     │ content     │    │ display_    │
     │ is_approved │    │ name        │
     └─────────────┘    └─────────────┘

     ┌──────────┐    ┌──────────┐
     │   Link   │    │ Setting  │
     │          │    │          │
     │ id       │    │ id       │
     │ name     │    │ key      │
     │ url      │    │ value    │
     │ sort_    │    │ desc     │
     │ order    │    └──────────┘
     └──────────┘
```

### Post 模型字段详解

| 字段 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `id` | Integer | 主键，自增 | - |
| `title` | String(200) | 文章标题 | 必填 |
| `slug` | String(200) | URL 别名（唯一） | 必填 |
| `summary` | String(500) | 文章摘要 | 空 |
| `content` | Text | Markdown 原文 | 必填 |
| `content_html` | Text | 渲染后的 HTML | 自动生成 |
| `cover_image` | String(500) | 封面图片 URL | 空 |
| `status` | String(20) | 状态 | `"draft"` |
| `is_top` | Boolean | 是否置顶 | `False` |
| `is_allow_comment` | Boolean | 是否允许评论 | `True` |
| `views` | Integer | 浏览次数 | `0` |
| `category_id` | Integer(FK) | 所属分类 ID | `None` |
| `created_at` | DateTime | 创建时间 | 自动 |
| `updated_at` | DateTime | 更新时间 | 自动 |
| `published_at` | DateTime | 发布时间 | 发布时设置 |

**状态流转：** `draft` → `published`（发布时自动设置 `published_at`）

### Comment 模型（支持嵌套回复）

```python
parent_id = Column(Integer, ForeignKey("comments.id"))  # 父评论 ID
replies = relationship("Comment", backref="parent", remote_side=[id])
```

- `parent_id = NULL` → 顶级评论
- `parent_id = 某评论 ID` → 回复
- `is_approved = False` → 待审核（默认）

---

## 4. API 接口文档

### 前台接口（`/api`）

无需认证，公开访问。

#### 文章

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| `GET` | `/api/posts` | 文章列表 | `page`, `page_size`, `category`, `tag`, `q` |
| `GET` | `/api/posts/{slug}` | 文章详情 | - |
| `GET` | `/api/posts/{post_id}/comments` | 文章评论 | - |

**文章列表响应示例：**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Hello World",
      "slug": "hello-world",
      "summary": "我的第一篇博客",
      "cover_image": "",
      "views": 42,
      "is_top": false,
      "category": {"id": 1, "name": "技术", "slug": "tech"},
      "tags": [{"id": 1, "name": "Python", "slug": "python"}],
      "published_at": "2026-05-10T10:00:00",
      "comment_count": 3
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3
}
```

#### 评论

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/comments` | 提交评论（需审核） |

**请求体：**
```json
{
  "post_id": 1,
  "parent_id": null,
  "author_name": "访客昵称",
  "author_email": "email@example.com",
  "author_website": "https://example.com",
  "content": "写得很好！"
}
```

#### 其他

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/categories` | 分类列表（含文章计数） |
| `GET` | `/api/tags` | 标签列表（含文章计数） |
| `GET` | `/api/links` | 友情链接 |
| `GET` | `/api/archives` | 归档（按年月分组） |

### 后台接口（`/admin/api`）

需要 JWT 认证（Bearer Token 或 Cookie）。

#### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/admin/api/login` | 登录，返回 JWT |
| `GET` | `/admin/api/me` | 当前用户信息 |

**登录请求：**
```json
{"username": "admin", "password": "admin123"}
```

**登录响应：**
```json
{"access_token": "eyJhbGciOiJIUzI1...", "token_type": "bearer"}
```

#### 仪表盘

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/admin/api/dashboard` | 统计数据 + 最近文章/评论 |

#### 文章管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/admin/api/posts` | 文章列表（含草稿） |
| `POST` | `/admin/api/posts` | 创建文章 |
| `GET` | `/admin/api/posts/{id}` | 文章详情 |
| `PUT` | `/admin/api/posts/{id}` | 更新文章 |
| `DELETE` | `/admin/api/posts/{id}` | 删除文章 |

**创建/更新请求体：**
```json
{
  "title": "文章标题",
  "slug": "article-slug",
  "summary": "摘要",
  "content": "# Markdown 内容\n\n正文...",
  "cover_image": "/uploads/cover.jpg",
  "status": "published",
  "is_top": false,
  "is_allow_comment": true,
  "category_id": 1,
  "tag_ids": [1, 2, 3]
}
```

#### 分类管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/admin/api/categories` | 列表 |
| `POST` | `/admin/api/categories` | 创建 |
| `PUT` | `/admin/api/categories/{id}` | 更新 |
| `DELETE` | `/admin/api/categories/{id}` | 删除 |

#### 标签管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/admin/api/tags` | 列表 |
| `POST` | `/admin/api/tags` | 创建 |
| `DELETE` | `/admin/api/tags/{id}` | 删除 |

#### 评论管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/admin/api/comments` | 评论列表 |
| `PUT` | `/admin/api/comments/{id}/approve` | 审核通过 |
| `DELETE` | `/admin/api/comments/{id}` | 删除评论 |

#### 友链管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/admin/api/links` | 列表 |
| `POST` | `/admin/api/links` | 创建 |
| `DELETE` | `/admin/api/links/{id}` | 删除 |

#### 系统设置

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/admin/api/settings` | 获取所有设置 |
| `PUT` | `/admin/api/settings` | 批量更新设置 |

---

## 5. 配置参数说明

### 环境变量列表

所有配置都以 `HALO_` 为前缀，通过环境变量或 `.env` 文件设置。

| 环境变量 | 类型 | 默认值 | 说明 |
|----------|------|--------|------|
| `HALO_APP_NAME` | string | `Halo Blog` | 应用名称 |
| `HALO_DEBUG` | bool | `false` | 调试模式（显示 SQL 日志） |
| `HALO_SECRET_KEY` | string | `change-me...` | **JWT 签名密钥（必须修改！）** |
| `HALO_HOST` | string | `0.0.0.0` | 监听地址 |
| `HALO_PORT` | int | `8000` | 监听端口 |
| `HALO_DATABASE_URL` | string | `sqlite+aiosqlite:///./data/blog.db` | 数据库连接字符串 |
| `HALO_ADMIN_USERNAME` | string | `admin` | 管理员用户名 |
| `HALO_ADMIN_PASSWORD` | string | `admin123` | **管理员密码（必须修改！）** |
| `HALO_BLOG_TITLE` | string | `My Blog` | 博客标题 |
| `HALO_BLOG_SUBTITLE` | string | `A personal blog...` | 博客副标题 |
| `HALO_BLOG_FOOTER` | string | `© 2026 Halo Blog...` | 页脚文字 |
| `HALO_POSTS_PER_PAGE` | int | `10` | 首页每页文章数 |
| `HALO_UPLOAD_DIR` | string | `uploads` | 上传文件目录 |
| `HALO_MAX_UPLOAD_SIZE` | int | `10485760` | 上传大小限制（字节，默认 10MB） |

### 修改配置的方法

#### 方法一：修改 `docker-compose.yml`（推荐）

```yaml
services:
  halo-blog:
    environment:
      - HALO_BLOG_TITLE=我的个人博客
      - HALO_BLOG_SUBTITLE=记录生活与技术
      - HALO_SECRET_KEY=my-super-secret-key-2026
      - HALO_ADMIN_PASSWORD=MySecureP@ss
      - HALO_POSTS_PER_PAGE=15
```

修改后重启容器：
```bash
cd E:\Docker\Halo_Docker
docker compose up -d
```

#### 方法二：创建 `.env` 文件

在项目根目录创建 `.env` 文件：

```env
HALO_BLOG_TITLE=我的个人博客
HALO_BLOG_SUBTITLE=记录生活与技术
HALO_SECRET_KEY=my-super-secret-key-2026
HALO_ADMIN_PASSWORD=MySecureP@ss
HALO_POSTS_PER_PAGE=15
HALO_DEBUG=true
```

然后在 `docker-compose.yml` 中引用：
```yaml
services:
  halo-blog:
    env_file:
      - .env
```

#### 方法三：直接修改 `src/config.py`

```python
class Settings(BaseSettings):
    blog_title: str = "我的个人博客"      # 修改默认值
    posts_per_page: int = 15              # 改为每页 15 篇
    max_upload_size: int = 20 * 1024 * 1024  # 改为 20MB
```

**注意：** 方法三需要重新构建镜像（`docker compose up -d --build`）。

---

## 6. Docker 部署指南

### Dockerfile 解析

```dockerfile
FROM python:3.12-slim              # 基础镜像

RUN apt-get install libjpeg zlib   # 系统依赖（图片处理）

COPY pyproject.toml ./             # 先复制依赖文件
RUN pip install .                  # 安装 Python 依赖（利用缓存）
COPY src/ ./src/                   # 最后复制源代码

EXPOSE 8000                        # 暴露端口
VOLUME ["/app/data", "/app/uploads"]  # 声明数据卷
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml 解析

```yaml
services:
  halo-blog:
    build: .                        # 从 Dockerfile 构建
    container_name: halo-blog       # 容器名称
    ports:
      - "8000:8000"                 # 端口映射
    volumes:
      - ./data:/app/data            # 数据库持久化
      - ./uploads:/app/uploads      # 上传文件持久化
    environment:                    # 环境变量配置
      - HALO_DEBUG=false
      - HALO_SECRET_KEY=change-this
      - HALO_ADMIN_PASSWORD=admin123
    restart: unless-stopped         # 自动重启
```

### 常用 Docker 命令

```bash
# 启动
cd E:\Docker\Halo_Docker
docker compose up -d

# 查看状态
docker ps --filter "name=halo-blog"

# 查看日志
docker logs halo-blog
docker logs -f halo-blog           # 实时跟踪

# 重启（应用配置变更后）
docker compose restart

# 重新构建（修改源代码后）
docker compose up -d --build

# 停止
docker compose down

# 停止并删除镜像
docker compose down --rmi all
```

### 数据备份

重要数据都在 `E:\Docker\Halo_Docker` 下的挂载卷中：

```bash
# 备份数据库
copy E:\Docker\Halo_Docker\data\blog.db E:\Backup\blog.db

# 备份上传文件
xcopy E:\Docker\Halo_Docker\uploads E:\Backup\uploads\ /E /I
```

---

## 7. 前端模板系统

### 模板继承结构

```
base.html                    ← 基础布局（Header + Nav + Footer）
├── index.html               ← 首页（文章列表 + 侧边栏）
├── post.html                ← 文章详情 + 评论区
├── archives.html            ← 归档页
├── categories.html          ← 分类页
└── links.html               ← 友链页

dashboard.html               ← 管理后台（独立 SPA）
```

### 前台页面数据加载方式

前台页面使用 **客户端渲染**，通过 JavaScript 调用 `/api` 接口：

```javascript
// 首页加载文章列表
const res = await fetch('/api/posts?page=1&page_size=10');
const data = await res.json();
// 渲染到 DOM
```

### 修改博客标题和副标题

在 `docker-compose.yml` 中修改环境变量：

```yaml
- HALO_BLOG_TITLE=我的技术博客
- HALO_BLOG_SUBTITLE=分享 Python 与 Docker 技术
```

### 修改页脚

```yaml
- HALO_BLOG_FOOTER=© 2026 我的博客. All rights reserved.
```

### 修改样式

编辑 `src/static/css/style.css`：

```css
:root {
    --primary: #2563eb;           /* 主题色（蓝色） */
    --primary-light: #3b82f6;     /* 悬停色 */
    --bg: #f8fafc;                /* 背景色 */
    --radius: 12px;               /* 圆角大小 */
    --shadow: 0 1px 3px rgba(0,0,0,0.06);  /* 阴影 */
}
```

修改后需要重新构建：`docker compose up -d --build`

---

## 8. 认证与安全

### JWT 认证流程

```
1. POST /admin/api/login
   → {"username": "admin", "password": "admin123"}
   ← {"access_token": "eyJ...", "token_type": "bearer"}

2. 后续请求携带 Token：
   Header: Authorization: Bearer eyJ...
   或 Cookie: access_token=eyJ...
```

### Token 配置

在 `src/services/auth.py` 中：

```python
ALGORITHM = "HS256"                    # 加密算法
ACCESS_TOKEN_EXPIRE_HOURS = 24         # Token 有效期（小时）
```

### 修改 Token 过期时间

编辑 `src/services/auth.py`：

```python
ACCESS_TOKEN_EXPIRE_HOURS = 48         # 改为 48 小时
```

### 密码安全

- 密码使用 `bcrypt` 哈希存储
- 首次启动自动创建管理员账号
- **生产环境必须修改 `HALO_SECRET_KEY` 和 `HALO_ADMIN_PASSWORD`**

### 评论审核机制

- 访客提交的评论默认 `is_approved = False`
- 管理员在后台审核通过后才显示
- 支持嵌套回复（`parent_id` 关联）

---

## 9. 常见修改指南

### 9.1 修改每页文章数量

**方法一：环境变量（推荐）**
```yaml
# docker-compose.yml
- HALO_POSTS_PER_PAGE=20
```

**方法二：修改代码**
```python
# src/config.py
posts_per_page: int = 20
```

### 9.2 修改上传文件大小限制

```python
# src/config.py
max_upload_size: int = 20 * 1024 * 1024  # 改为 20MB
```

### 9.3 添加新的页面

1. 创建模板文件 `src/templates/theme/newpage.html`
2. 在 `src/main.py` 添加路由：

```python
@app.get("/newpage", response_class=HTMLResponse)
async def new_page(request: Request):
    return templates.TemplateResponse(request, "theme/newpage.html", {"settings": settings})
```

3. 在 `base.html` 的导航栏添加链接：

```html
<nav class="site-nav">
    <a href="/" class="nav-link">首页</a>
    <a href="/newpage" class="nav-link">新页面</a>  <!-- 添加 -->
</nav>
```

### 9.4 修改 Markdown 渲染扩展

编辑 `src/services/post_service.py`：

```python
content_html = markdown.markdown(
    data.content,
    extensions=[
        "fenced_code",      # 围栏代码块
        "tables",           # 表格
        "codehilite",       # 代码高亮
        "toc",              # 目录
        "footnotes",        # 脚注（可添加）
        "attr_list",        # 属性列表（可添加）
    ]
)
```

### 9.5 修改 JWT 过期时间

编辑 `src/services/auth.py`：

```python
ACCESS_TOKEN_EXPIRE_HOURS = 72    # 改为 72 小时
# 或使用分钟
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 分钟
```

### 9.6 修改主题色

编辑 `src/static/css/style.css`：

```css
:root {
    --primary: #10b981;         /* 改为绿色 */
    --primary-light: #34d399;
}
```

### 9.7 禁用评论系统

全局禁用：编辑 `src/domain/models.py`：

```python
class Post(Base):
    is_allow_comment = Column(Boolean, default=False)  # 默认关闭评论
```

### 9.8 切换到 PostgreSQL

1. 修改 `docker-compose.yml`，添加 PostgreSQL 服务：

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: haloblog
      POSTGRES_USER: halo
      POSTGRES_PASSWORD: halo123
    volumes:
      - pgdata:/var/lib/postgresql/data

  halo-blog:
    environment:
      - HALO_DATABASE_URL=postgresql+asyncpg://halo:halo123@db:5432/haloblog
    depends_on:
      - db

volumes:
  pgdata:
```

2. 修改 `pyproject.toml` 依赖：

```toml
dependencies = [
    # 替换 aiosqlite 为 asyncpg
    "asyncpg>=0.29.0",
]
```

3. 修改 `Dockerfile`：

```dockerfile
# 替换 aiosqlite 安装
RUN pip install --no-cache-dir asyncpg
```

4. 重新构建：`docker compose up -d --build`

---

## 10. 故障排查

### 容器无法启动

```bash
# 查看日志
docker logs halo-blog

# 常见原因：
# 1. 端口被占用 → 修改 ports 映射
# 2. 数据库锁定 → 删除 data/blog.db
# 3. 依赖安装失败 → docker compose build --no-cache
```

### 500 Internal Server Error

```bash
# 查看详细日志
docker logs halo-blog 2>&1 | tail -20

# 常见原因：
# 1. 模板语法错误
# 2. 数据库表不存在 → 重启容器自动建表
# 3. 配置格式错误
```

### 评论不显示

- 新提交的评论默认 `is_approved = False`
- 需要管理员在后台审核通过
- API 只返回 `is_approved = True` 的评论

### 忘记管理员密码

修改 `docker-compose.yml` 中的密码，重启：

```yaml
- HALO_ADMIN_PASSWORD=newpassword
```

然后执行：`docker compose up -d`

### 数据库重置

```bash
docker compose down
del E:\Docker\Halo_Docker\data\blog.db
docker compose up -d
```

---

## 附录：依赖清单

| 包名 | 版本 | 用途 |
|------|------|------|
| `fastapi` | ≥0.115.0 | Web 框架 |
| `uvicorn` | ≥0.32.0 | ASGI 服务器 |
| `sqlalchemy` | ≥2.0.36 | ORM |
| `aiosqlite` | ≥0.20.0 | SQLite 异步驱动 |
| `pydantic` | ≥2.10.0 | 数据验证 |
| `pydantic-settings` | ≥2.6.0 | 配置管理 |
| `jinja2` | ≥3.1.4 | 模板引擎 |
| `markdown` | ≥3.7 | Markdown 渲染 |
| `python-jose` | ≥3.3.0 | JWT 生成/验证 |
| `passlib` | ≥1.7.4 | 密码哈希 |
| `bcrypt` | ≥4.0,<5.0 | 加密算法 |
| `python-slugify` | ≥8.0.4 | URL 别名生成 |
| `python-multipart` | ≥0.0.12 | 表单解析 |
| `aiofiles` | ≥24.1.0 | 异步文件操作 |
| `Pillow` | ≥10.4.0 | 图片处理 |

---

*文档生成时间：2026-05-10 | 项目路径：E:\Docker\Halo_Docker*
