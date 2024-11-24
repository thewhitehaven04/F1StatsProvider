from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.laps import SessionRouter
from routers.event import EventRouter


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_methods=["GET", "POST"],
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
)
app.include_router(SessionRouter)
app.include_router(EventRouter)
