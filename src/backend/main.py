from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.search import _dispatcher, router as search_router
from config import settings
from logger import setup_logging, logger

# Initialize logging
setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("NebulaTorrent API starting up...")

@app.get("/")
async def root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "plugins_loaded": len(_dispatcher.plugins)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.DEBUG
    )
