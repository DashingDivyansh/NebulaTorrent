import json
from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Optional
from search.dispatcher import SearchDispatcher
from db.database import db
from config import settings
from logger import logger

router = APIRouter()

# Initialize dispatcher globally for the router module
# In a larger app, we might use dependencies or app.state
_dispatcher = SearchDispatcher(settings.PLUGINS_DIR)
_dispatcher.load_plugins()

@router.get("/search")
async def search(
    request: Request,
    q: str = Query(..., min_length=1),
    category: Optional[str] = None
):
    # Record history
    try:
        db.add_search_history(q, category)
    except Exception as e:
        logger.error(f"Failed to record history: {e}")

    async def event_generator():
        try:
            if not _dispatcher.plugins:
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return

            async for event in _dispatcher.stream_search(q, category):
                if await request.is_disconnected():
                    logger.info("Search client disconnected")
                    break

                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Critical error in search stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/plugins")
async def list_plugins():
    return _dispatcher.plugin_health()

@router.get("/history")
async def get_history(limit: int = 20):
    try:
        return db.get_search_history(limit)
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        raise HTTPException(status_code=500, detail="Database error")
