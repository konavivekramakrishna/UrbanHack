import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database import engine, Base
from src.routers import user, match
import redis.asyncio as redis

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis client and attach it to app state
    app.state.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    # Create database tables on startup.
    Base.metadata.create_all(bind=engine)
    yield
    # Close Redis connection on shutdown.
    await app.state.redis.close()

app = FastAPI(title="Marriage Matchmaking API", lifespan=lifespan)

# Include routers
app.include_router(user.router, tags=["users"])
app.include_router(match.router, tags=["matches"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Marriage Matchmaking API!"}
