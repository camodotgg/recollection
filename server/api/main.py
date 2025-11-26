"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from server.db.database import init_db
from server.api.routes import auth, content, courses, tasks, websocket_routes, progress
from server.api.redis_listener import redis_listener


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize database
    print("=== Initializing database...")
    await init_db()
    print("=== Database initialized")

    # Start Redis pub/sub listener for WebSocket updates
    print("=== Starting Redis listener...")
    try:
        await redis_listener.start()
        print("=== Redis listener started successfully")
    except Exception as e:
        print(f"=== ERROR starting Redis listener: {e}")
        import traceback
        traceback.print_exc()

    yield

    # Shutdown: Clean up resources
    print("=== Stopping Redis listener...")
    await redis_listener.stop()
    print("=== Redis listener stopped")


# Create FastAPI application
app = FastAPI(
    title="Recollection API",
    description="API for content loading and course generation",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(courses.router)
app.include_router(tasks.router)
app.include_router(websocket_routes.router)
app.include_router(progress.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Recollection API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
