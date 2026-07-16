import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_signup(async_client: AsyncClient):
    response = await async_client.post(
        "/users/signup",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_signup_duplicate(async_client: AsyncClient):
    await async_client.post(
        "/users/signup",
        json={
            "username": "testuser2",
            "email": "testuser2@example.com",
            "password": "testpassword"
        }
    )
    
    response = await async_client.post(
        "/users/signup",
        json={
            "username": "testuser2",
            "email": "testuser3@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    await async_client.post(
        "/users/signup",
        json={
            "username": "logintest",
            "email": "logintest@example.com",
            "password": "mypassword"
        }
    )
    
    response = await async_client.post(
        "/users/login",
        data={
            "username": "logintest",
            "password": "mypassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_fail(async_client: AsyncClient):
    response = await async_client.post(
        "/users/login",
        data={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_read_profile(async_client: AsyncClient):
    await async_client.post(
        "/users/signup",
        json={
            "username": "profileuser",
            "email": "profileuser@example.com",
            "password": "password"
        }
    )
    login_response = await async_client.post(
        "/users/login",
        data={
            "username": "profileuser",
            "password": "password"
        }
    )
    token = login_response.json()["access_token"]
    
    response = await async_client.get(
        "/users/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "profileuser"
