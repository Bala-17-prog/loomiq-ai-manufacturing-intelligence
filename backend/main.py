from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.logging_config import logger
from backend.routes import dashboard
from backend.routes import production
from backend.routes import machines
from backend.routes import quality
from backend.routes import copilot
from backend.routes import simulator
import os

app = FastAPI(
    title="LoomIQ",
    description="AI-Powered Textile Manufacturing Intelligence",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.getenv("VERCEL") == "1":
    IMAGE_DIR = "/tmp/loomiq_images"
    STATIC_IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fabric_images")
    try:
        os.makedirs(os.path.join(IMAGE_DIR, "raw"), exist_ok=True)
        os.makedirs(os.path.join(IMAGE_DIR, "processed"), exist_ok=True)
    except OSError:
        pass
    app.mount("/api/runtime_images", StaticFiles(directory=IMAGE_DIR), name="runtime_images")
    if os.path.exists(STATIC_IMAGE_DIR):
        app.mount("/images", StaticFiles(directory=STATIC_IMAGE_DIR), name="images")
else:
    IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fabric_images")
    try:
        os.makedirs(IMAGE_DIR, exist_ok=True)
    except OSError:
        pass
    app.mount("/images", StaticFiles(directory=IMAGE_DIR), name="images")

app.include_router(dashboard.router)
app.include_router(production.router)
app.include_router(machines.router)
app.include_router(quality.router)
app.include_router(copilot.router)
app.include_router(simulator.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting LoomIQ API...")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Mount Frontend at root
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
