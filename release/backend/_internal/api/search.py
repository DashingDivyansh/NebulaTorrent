import asyncio
import json
from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional
from models.torrent import TorrentResult
from search.dispatcher import SearchDispatcher
from db.database import db
from config import settings
from logger import logger
import os

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
            tasks = [plugin.search(q, category) for plugin in _dispatcher.plugins]
            if not tasks:
                yield "data: []\n\n"
                yield "data: [DONE]\n\n"
                return

            pending = set(asyncio.create_task(t) for t in tasks)
            
            while pending:
                # Client disconnected check
                if await request.is_disconnected():
                    logger.info("Search client disconnected, cancelling tasks")
                    for task in pending:
                        task.cancel()
                    break

                done, pending = await asyncio.wait(
                    pending, 
                    return_when=asyncio.FIRST_COMPLETED, 
                    timeout=1.0 # Short timeout for frequent disconnect checks
                )
                
                for task in done:
                    try:
                        results = await task
                        if results and isinstance(results, list):
                            data_list = []
                            for r in results:
                                # Safe serialization
                                data_list.append(r.model_dump() if hasattr(r, 'model_dump') else r.dict())
                            
                            yield f"data: {json.dumps(data_list)}\n\n"
                    except asyncio.CancelledError:
                        continue
                    except Exception as e:
                        logger.error(f"Plugin search error: {e}")
                
                # Keep-alive heartbeat
                if not done and pending:
                    yield ": heartbeat\n\n"
            
            if not await request.is_disconnected():
                yield "data: [DONE]\n\n"
                
        except Exception as e:
            logger.error(f"Critical error in search stream: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

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
    return [{"name": p.name, "version": p.version} for p in _dispatcher.plugins]

@router.get("/history")
async def get_history(limit: int = 20):
    try:
        return db.get_search_history(limit)
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        raise HTTPException(status_code=500, detail="Database error")
