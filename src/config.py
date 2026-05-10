"""Application configuration.

Copyright (c) 2026 ArcaneCoreX-dev - MIT License
See LICENSE file for details.
"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "Halo Blog"
    app_version: str = "0.1.0"
    debug: bool = False
    secret_key: str = "change-me-in-production-please"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/blog.db"

    # Admin
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # Blog
    blog_title: str = "My Blog"
    blog_subtitle: str = "A personal blog powered by Halo Blog"
    blog_footer: str = "© 2026 Halo Blog. All rights reserved."
    posts_per_page: int = 10

    # Upload
    upload_dir: str = "uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    model_config = {"env_prefix": "HALO_", "env_file": ".env"}


settings = Settings()

# Ensure data & upload dirs exist
Path("data").mkdir(exist_ok=True)
Path(settings.upload_dir).mkdir(exist_ok=True)

# Footer branding
FOOTER_HTML = '<p class="footer-brand">Powered by <a href="https://github.com" target="_blank">Halo Blog</a> &copy; 2026 ArcaneCoreX-dev</p>'
