from fastapi import FastAPI
from users.router import router as users_router
from products.router import router as products_router
from db import engine, Base
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="FastAPI Async Auth", lifespan=lifespan)

app.include_router(users_router)
app.include_router(products_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI Async Auth API"}
