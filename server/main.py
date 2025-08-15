from config import settings

try:
    from fastapi import FastAPI
    import uvicorn
except ImportError:
    print("Error: Required packages not installed. Please install fastapi and uvicorn:")
    print("pip install fastapi uvicorn")
    exit(1)

# Create FastAPI app
app = FastAPI(
    title="Chat Application API",
    description="A simple chat application backend",
    version="1.0.0",
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Chat Application API is running", "status": "healthy"}

if __name__ == "__main__":
    print(f"Server listening on port {settings.API_PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.API_PORT,
        reload=False,
        log_level="info"
    )