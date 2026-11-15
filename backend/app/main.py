"""
ARES Mission Control - FastAPI Application Entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router
from backend.app.api.route_api import router as route_planning_router

app = FastAPI(
    title="ARES Planetary Mission Control API",
    description="Scientific API for Mars exploration, MOLA cartography, and autonomous route intelligence.",
    version="1.0.0"
)

# CORS configuration for React frontend local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev (Vite default :5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(route_planning_router)


@app.get("/")
def root():
    return {
        "message": "ARES Mission Control API operational",
        "docs_url": "/docs",
        "status_url": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

