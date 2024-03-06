from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contacts.routes import router as contacts_router 
from users.routes import auth_router, user_router
from app.settings import BASE_URL_PREFIX, APP_HOST, APP_PORT, REDIS_PORT, REDIS_HOST
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    r = await redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, encoding='utf-8', decode_responses=True)
    await FastAPILimiter.init(r)
    yield

origins = [ "http://localhost:3000" ]

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

routers = [auth_router, user_router, contacts_router]

[app.include_router(router, prefix=BASE_URL_PREFIX) for router in routers]

@app.get('/')
def read_root():
    return {"message": "Contact app!"}
    
    
if __name__ == "__main__":
    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=True)