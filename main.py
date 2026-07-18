from fastapi import FastAPI
from users.router import router as users_router
from products.router import router as products_router
from posts.router import router as posts_router
from db import engine, Base
import users.models
import products.models
import posts.models
from redis_client import init_redis, close_redis
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await close_redis()

app = FastAPI(title="FastAPI Async Auth", lifespan=lifespan)

app.include_router(users_router)
app.include_router(products_router)
app.include_router(posts_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI Async Auth API"}
