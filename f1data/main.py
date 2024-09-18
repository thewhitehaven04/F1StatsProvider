from fastapi import FastAPI

from routers.laps import SessionRouter


app = FastAPI()

app.include_router(SessionRouter)