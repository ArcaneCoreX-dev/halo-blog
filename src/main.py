"""Halo Blog — main application entry point.

Copyright (c) 2026 ArcaneCoreX-dev - MIT License
See LICENSE file for details.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.adapters.database import async_session, init_db
from src.api.admin_routes import router as admin_router
from src.api.blog_routes import router as blog_router
from src.config import settings
from src.services.auth import ensure_admin

BASE_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    async with async_session() as db:
        await ensure_admin(db)
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A lightweight personal blog system built with Python, similar to Halo CMS.",
    lifespan=lifespan,
    contact={"name": "ArcaneCoreX-dev", "url": "https://github.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

# Static files & templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/uploads", StaticFiles(directory=str(Path(settings.upload_dir))), name="uploads")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API routes
app.include_router(blog_router)
app.include_router(admin_router)


# ── Page routes (SSR with Jinja2) ────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "theme/index.html", {"settings": settings})


@app.get("/archives", response_class=HTMLResponse)
async def archives_page(request: Request):
    return templates.TemplateResponse(request, "theme/archives.html", {"settings": settings})


@app.get("/post/{slug}", response_class=HTMLResponse)
async def post_detail(request: Request, slug: str):
    return templates.TemplateResponse(request, "theme/post.html", {"settings": settings, "slug": slug})


@app.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request):
    return templates.TemplateResponse(request, "theme/categories.html", {"settings": settings})


@app.get("/links", response_class=HTMLResponse)
async def links_page(request: Request):
    return templates.TemplateResponse(request, "theme/links.html", {"settings": settings})


# ── Admin SPA ────────────────────────────────────────
@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/{path:path}", response_class=HTMLResponse)
async def admin_spa(request: Request, path: str = ""):
    return templates.TemplateResponse(request, "admin/dashboard.html", {"settings": settings})


# ── Upload endpoint ──────────────────────────────────
@app.post("/admin/api/upload")
async def upload_file(request: Request):
    from fastapi import UploadFile, File, Depends
    from src.services.auth import get_current_user
    from src.domain.models import User
    import uuid, aiofiles

    # This is handled inline to avoid circular imports
    form = await request.form()
    file: UploadFile = form.get("file")  # type: ignore
    if not file:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No file uploaded")

    ext = Path(file.filename or "file").suffix
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = Path(settings.upload_dir) / filename

    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    return {"url": f"/uploads/{filename}", "filename": filename}
