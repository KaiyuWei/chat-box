import logging

from config import settings
from database import test_connection
from routers import user_router

# config logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# import required packages
try:
    import uvicorn
    from fastapi import APIRouter, FastAPI
except ImportError:
    logger.error("Error: Required packages not installed.")
    exit(1)

app = FastAPI(
    title="Chat Application API",
    description="A simple chat application backend",
    version="1.0.0",
)


# check database connection
@app.on_event("startup")
async def startup_event():
    """Test database connection on startup"""

    if not test_connection():
        logger.error("Failed to connect to database. Exiting...")
        exit(1)

    logger.info("Database connection successful")


# configure API router
api_router = APIRouter(prefix="/api")
api_router.include_router(user_router)

app.include_router(api_router)

# start up the server
if __name__ == "__main__":
    logger.info(f"Server listening on port {settings.API_PORT}")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.API_PORT,
        reload=False,
        log_level="info",
    )
