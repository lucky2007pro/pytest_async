from products.schema import ProductCreateSchema, ProductOutSchema, ProductUpdateSchema
from products.crud import create_product, list_product, delete_product, update_product, detail_product
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db

router = APIRouter()

@router.post("/create")
async def create_product_router(data: ProductCreateSchema, db: AsyncSession = Depends(get_db)):
    return await create_product(data, db)

@router.get("/list")
async def list_product_router(db: AsyncSession = Depends(get_db)):
    return await list_product(db)

@router.get("/detail/{id}")
async def detail_product_router(id: int, db: AsyncSession = Depends(get_db)):
    return await detail_product(id, db)

@router.put("/update/{id}")
async def update_product_router(id: int, data: ProductUpdateSchema, db: AsyncSession = Depends(get_db)):
    return await update_product(id, data, db)

@router.delete("/delete/{id}")
async def delete_product_router(id: int, db: AsyncSession = Depends(get_db)):
    return await delete_product(id, db)