from datetime import datetime
import time
from fastapi import FastAPI, Request
from fastapi import logger
from fastapi.middleware.cors import CORSMiddleware

from routers.session_laps import SessionRouter
from routers.session_results import SessionResults
from routers.event import EventRouter


app = FastAPI()
logger.logger.setLevel(5)


@app.middleware("http")
async def logger_middleware(request: Request, next):
    start = time.perf_counter()
    logger.logger.warning(
        f"------------------\nProcessing request to endpoint: {request.url}"
    )
    logger.logger.warning(f"Params: {request.query_params}")
    logger.logger.warning(f"Body: {await request.body()}")
    logger.logger.warning(
        f"Processing started: {datetime.isoformat(datetime.now(), timespec='milliseconds')}"
    )
    response = await next(request)
    logger.logger.warning(
        f"Processing finished: {datetime.isoformat(datetime.now(), timespec='milliseconds')}, in {time.perf_counter() - start:.3f}\n-------"
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_methods=["GET", "POST"],
    allow_origins=["*"],
    allow_credentials=True,
)
app.include_router(SessionRouter)
app.include_router(SessionResults)
app.include_router(EventRouter)
