from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.session_laps import SessionRouter
from routers.session_results import SessionResults
from routers.event import EventRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield 
    # prefetch_recent_events()

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