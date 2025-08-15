from config import settings
from routers import auth

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

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)


# for health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}


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
