import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test123!",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "duplicateuser",
            "email": "dup@example.com",
            "password": "Test123!",
        }
    )
    
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "duplicateuser",
            "email": "dup2@example.com",
            "password": "Test123!",
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "Test123!",
        }
    )
    
    response = await client.post(
        "/api/auth/login",
        json={
            "login": "loginuser",
            "password": "Test123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={
            "login": "nonexistent",
            "password": "Wrong123!"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "meuser",
            "email": "me@example.com",
            "password": "Test123!",
        }
    )
    
    login_response = await client.post(
        "/api/auth/login",
        json={
            "login": "meuser",
            "password": "Test123!"
        }
    )
    
    access_token = login_response.json()["access_token"]
    
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "meuser"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "refreshuser",
            "email": "refresh@example.com",
            "password": "Test123!",
        }
    )
    
    login_response = await client.post(
        "/api/auth/login",
        json={
            "login": "refreshuser",
            "password": "Test123!"
        }
    )
    
    refresh_token = login_response.json()["refresh_token"]
    
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
