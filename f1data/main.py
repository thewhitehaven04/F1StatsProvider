from asyncio import create_task
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.session_laps import SessionRouter
from routers.session_results import SessionResults
from routers.event import EventRouter
from services.prefetcher.load_recent import load_recent

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_task(load_recent())
    yield 

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_methods=["GET", "POST"],
    allow_origins=["*"],
    allow_credentials=True,
)
app.include_router(SessionRouter)
app.include_router(SessionResults)
app.include_router(EventRouter)