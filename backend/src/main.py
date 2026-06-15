"""LexRedline Contract Engine - FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.routes import router

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

# CORS middleware (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info."""
    return {
        "service": "LexRedline Contract Engine",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "GET /api/v1/health",
            "models": "GET /api/v1/models",
            "clauses": "GET /api/v1/clauses",
            "analyze_file": "POST /api/v1/analyze/file",
            "analyze_text": "POST /api/v1/analyze/text",
        }
    }


def start():
    """Start the server (convenience for development)."""
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
    )


if __name__ == "__main__":
    start()