"""
ARES Mission Control - FastAPI Application Entrypoint
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.api.routes import router
from backend.app.api.route_api import router as route_planning_router

app = FastAPI(
    title="ARES Planetary Mission Control API",
    description="Scientific API for Mars exploration, MOLA cartography, and autonomous route intelligence.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(route_planning_router)

# Mount compiled Svelte production frontend if present
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend-svelte" / "dist"
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        target_file = FRONTEND_DIST / full_path
        if target_file.is_file():
            return FileResponse(str(target_file))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "message": "ARES Mission Control API operational",
            "docs_url": "/docs",
            "status_url": "/api/health"
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", os.environ.get("ARES_PORT", 8001)))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=False)


