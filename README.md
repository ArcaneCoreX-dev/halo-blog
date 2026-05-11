# 🌟 Halo Blog

> A lightweight personal blog system built with Python, inspired by [Halo CMS](https://halo.run/).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## ✨ Features

- 📝 **文章管理** — Markdown 编辑器 + 实时预览
- 📂 **分类系统** — 文章分类管理
- 🏷️ **标签系统** — 标签云 + 标签筛选 + 写文章时选择标签
- 💬 **评论系统** — 访客评论 + 管理员审核 + 嵌套回复
- 🔗 **友情链接** — 友链管理
- 📊 **数据仪表盘** — 统计概览
- 👤 **个人信息** — 修改显示名称、邮箱、头像、密码
- 🔐 **JWT 认证** — 安全的管理后台
- 📱 **响应式设计** — 移动端友好
- 🐳 **Docker 部署** — 一键启动
- 🏷️ **动态标题** — 博客标题自动显示管理员名称

## 🚀 Quick Start

### Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/ArcaneCoreX-dev/halo-blog.git
cd halo-blog

# Start the application
docker compose up -d

# Access the application
# Frontend: http://localhost:8000
# Admin:    http://localhost:8000/admin
# Default:  admin / admin123
```

### Local Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env

# Start the server
uvicorn src.main:app --reload --port 8000
```

### Windows One-Click

Double-click `一键启动.bat` to start automatically.

## 📸 Screenshots

> Add screenshots here after deployment

```
┌─────────────────────────────────────────┐
│  🏠 首页                                │
│  ┌─────────────────────────────────┐    │
│  │  文章列表 + 侧边栏              │    │
│  │  ┌───────┐ ┌───────┐           │    │
│  │  │ 文章1 │ │ 文章2 │  ...      │    │
│  │  └───────┘ └───────┘           │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## 📁 Project Structure

```
halo-blog/
├── src/
│   ├── main.py              # Application entry point
│   ├── config.py             # Configuration management
│   ├── domain/
│   │   ├── models.py         # SQLAlchemy ORM models
│   │   └── schemas.py        # Pydantic schemas
│   ├── adapters/
│   │   └── database.py       # Database engine & session
│   ├── services/
│   │   ├── post_service.py   # Post CRUD operations
│   │   ├── comment_service.py# Comment management
│   │   └── auth.py           # JWT authentication
│   ├── api/
│   │   ├── blog_routes.py    # Public API endpoints
│   │   └── admin_routes.py   # Admin API endpoints
│   ├── templates/            # Jinja2 templates
│   └── static/               # CSS & JavaScript
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## ⚙️ Configuration

All configuration is done via environment variables with `HALO_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `HALO_SECRET_KEY` | `change-me` | JWT signing secret |
| `HALO_ADMIN_USERNAME` | `admin` | Admin username |
| `HALO_ADMIN_PASSWORD` | `change-me` | Admin password |
| `HALO_BLOG_TITLE` | `My Blog` | Blog title |
| `HALO_BLOG_SUBTITLE` | `A personal blog...` | Blog subtitle |
| `HALO_POSTS_PER_PAGE` | `10` | Posts per page |
| `HALO_DEBUG` | `false` | Debug mode |

See [`.env.example`](.env.example) for all available options.

## 📡 API Documentation

The API follows RESTful conventions. Access interactive docs at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Public Endpoints

```
GET    /api/posts              # List posts (paginated)
GET    /api/posts/{slug}       # Get post by slug
GET    /api/categories         # List categories
GET    /api/tags               # List tags
GET    /api/archives           # Archives by month
GET    /api/links              # Friendship links
POST   /api/comments           # Submit comment
```

### Admin Endpoints (JWT Required)

```
POST   /admin/api/login        # Login
GET    /admin/api/dashboard    # Dashboard stats
CRUD   /admin/api/posts        # Post management
CRUD   /admin/api/categories   # Category management
CRUD   /admin/api/tags         # Tag management
CRUD   /admin/api/comments     # Comment management
CRUD   /admin/api/links        # Link management
GET/PUT /admin/api/settings    # System settings
```

## 🛠️ Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Lint
ruff check .

# Format
ruff format .

# Type check
mypy src/

# Run tests
pytest --cov=src
```

## 📦 Deployment

### Production Checklist

1. Change `HALO_SECRET_KEY` to a random string
2. Change `HALO_ADMIN_PASSWORD`
3. Set `HALO_DEBUG=false`
4. Configure reverse proxy (Nginx)
5. Enable HTTPS

### Docker Commands

```bash
docker compose up -d              # Start
docker compose restart            # Restart
docker compose up -d --build      # Rebuild
docker compose down               # Stop
docker logs halo-blog             # View logs
```

## 📄 Documentation

- [项目技术文档](docs/PROJECT_DOCUMENTATION.md) — Architecture, API, Database
- [管理后台操作手册](docs/OPERATIONS_MANUAL.md) — Admin guide, Configuration
- [部署教程](docs/DEPLOYMENT.md) — Step-by-step deployment

## 🤝 Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Halo CMS](https://halo.run/) — Inspiration
- [FastAPI](https://fastapi.tiangolo.com/) — Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM
- [Jinja2](https://jinja.palletsprojects.com/) — Template engine

---

<p align="center">
  <small>© 2026 ArcaneCoreX-dev | <a href="https://github.com/ArcaneCoreX-dev/">GitHub</a></small>
</p>
