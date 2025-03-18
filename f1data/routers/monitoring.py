
from fastapi import APIRouter

from services.prefetcher.load_recent import prefetch_recent_events


MonitoringRouter = APIRouter(prefix="/monitroing", tags=["Monitoring"])

@MonitoringRouter.post('/fetchRecent')
async def fetch_recent_events():
    await prefetch_recent_events()
    return None
    