import logging

from chat_model_loader import load_model_and_processor
from config import settings
from database import test_connection
from routers import chat_model_router, user_router, conversation_router

# config logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# import required packages
try:
    import uvicorn
    from fastapi import APIRouter, FastAPI
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    logger.error("Error: Required packages not installed.")
    exit(1)

app = FastAPI(
    title="Chat Application API",
    description="A simple chat application backend",
    version="1.0.0",
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# check database connection
@app.on_event("startup")
async def startup_event():
    """Test database connection and load model on startup"""

    if not test_connection():
        logger.error("Failed to connect to database. Exiting...")
        exit(1)

    logger.info("Database connection successful")

    logger.info("Loading chat model...")
    load_model_and_processor()
    logger.info("Chat model and processor loaded successfully")


# configure API router
api_router = APIRouter(prefix="/api")
api_router.include_router(user_router)
api_router.include_router(chat_model_router)
api_router.include_router(conversation_router)

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
