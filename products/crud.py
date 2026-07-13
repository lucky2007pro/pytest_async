from unittest import result

from products.schema import ProductCreateSchema, ProductUpdateSchema, ProductOutSchema
from sqlalchemy.ext.asyncio import AsyncSession
from products.models import Product
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy import select

async def create_product(data: ProductCreateSchema, db: AsyncSession):
    product = Product(**data.model_dump())

    db.add(product)

    await db.commit()
    await db.refresh(product)

    return {
        'msg': "Product created",
        'status': status.HTTP_201_CREATED,
        'data': ProductOutSchema.model_validate(product)
    }

async def list_product(db: AsyncSession):
    query = select(Product)
    result = await db.execute(query)
    products = result.scalars().all()

    return {
        'msg': 'Product list',
        'count': len(products),
        'status': status.HTTP_200_OK,
        'data': products
    }

async def detail_product(id:int, db: AsyncSession):
    query = select(Product).where(
        Product.id == id
    )
    result = await db.execute(query)

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found"
        )
    return product

async def delete_product(id:int, db: AsyncSession):
    product = await detail_product(id, db)

    await db.delete(product)
    await db.commit()

    return {
        'msg': f"Product with id {id} deleted",
        'status': status.HTTP_200_OK
    }

async def update_product(id:int, data: ProductUpdateSchema, db: AsyncSession):
    product = await detail_product(id, db)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return {
        'msg': f"Product with id {id} updated",
        'status': status.HTTP_200_OK,
        'data': ProductOutSchema.model_validate(product)
    }