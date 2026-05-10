"""API integration tests.

Copyright (c) 2026 ArcaneCoreX-dev - MIT License
See LICENSE file for details.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_returns_200(client: AsyncClient):
    """Test that the homepage loads."""
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_api_posts_empty(client: AsyncClient):
    """Test that posts API returns empty list initially."""
    response = await client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_api_categories_empty(client: AsyncClient):
    """Test that categories API returns empty list initially."""
    response = await client.get("/api/categories")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_tags_empty(client: AsyncClient):
    """Test that tags API returns empty list initially."""
    response = await client.get("/api/tags")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_archives_empty(client: AsyncClient):
    """Test that archives API returns empty dict initially."""
    response = await client.get("/api/archives")
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.asyncio
async def test_admin_login_success(client: AsyncClient, admin_token: str):
    """Test admin login returns valid token."""
    assert admin_token is not None
    assert len(admin_token) > 0


@pytest.mark.asyncio
async def test_admin_login_failure(client: AsyncClient):
    """Test admin login with wrong credentials."""
    response = await client.post(
        "/admin/api/login",
        json={"username": "wrong", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_dashboard(client: AsyncClient, admin_token: str):
    """Test admin dashboard returns stats."""
    response = await client.get(
        "/admin/api/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert data["stats"]["posts"] == 0


@pytest.mark.asyncio
async def test_admin_create_post(client: AsyncClient, admin_token: str):
    """Test creating a post via admin API."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.post(
        "/admin/api/posts",
        json={
            "title": "Test Post",
            "slug": "test-post",
            "content": "# Hello World\n\nThis is a test.",
            "status": "published",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["slug"] == "test-post"


@pytest.mark.asyncio
async def test_admin_unauthorized(client: AsyncClient):
    """Test that admin API requires authentication."""
    response = await client.get("/admin/api/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_post_not_found(client: AsyncClient):
    """Test that non-existent post returns 404."""
    response = await client.get("/api/posts/non-existent-slug")
    assert response.status_code == 404
