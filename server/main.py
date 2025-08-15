import logging

from config import settings
from database import test_connection
from routers import auth

# TODO: Add logging in production env.

try:
    import uvicorn
    from fastapi import APIRouter, FastAPI
except ImportError:
    print("Error: Required packages not installed. Please install fastapi and uvicorn:")
    print("pip install fastapi uvicorn")
    exit(1)

app = FastAPI(
    title="Chat Application API",
    description="A simple chat application backend",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Test database connection on startup"""

    if not test_connection():
        print("Failed to connect to database. Exiting...")
        exit(1)

    print("Database connection successful")


api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)

app.include_router(api_router)

if __name__ == "__main__":
    print(f"Server listening on port {settings.API_PORT}")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.API_PORT,
        reload=False,
        log_level="info",
    )
