import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_product(async_client: AsyncClient):
    response = await async_client.post(
        "/create",
        json={
            "title": "Test Product",
            "desc": "Test Description",
            "price": "99.99"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 201
    assert data["msg"] == "Product created"
    assert data["data"]["title"] == "Test Product"

@pytest.mark.asyncio
async def test_create_product_invalid_price(async_client: AsyncClient):
    response = await async_client.post(
        "/create",
        json={
            "title": "Invalid Price Product",
            "price": "-10.0"
        }
    )
    assert response.status_code == 422 # Pydantic Validation Error

@pytest.mark.asyncio
async def test_create_product_invalid_title(async_client: AsyncClient):
    response = await async_client.post(
        "/create",
        json={
            "title": "12345",
            "price": "10.0"
        }
    )
    assert response.status_code == 422 # Pydantic Validation Error

@pytest.mark.asyncio
async def test_list_products(async_client: AsyncClient):
    # Setup - create a product
    await async_client.post(
        "/create",
        json={
            "title": "Listable Product",
            "price": "15.0"
        }
    )
    
    response = await async_client.get("/list")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1

@pytest.mark.asyncio
async def test_detail_product(async_client: AsyncClient):
    # Setup - create product
    create_response = await async_client.post(
        "/create",
        json={
            "title": "Detail Product",
            "price": "20.0"
        }
    )
    product_id = create_response.json()["data"]["id"]
    
    # Get Detail
    response = await async_client.get(f"/detail/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Detail Product"
