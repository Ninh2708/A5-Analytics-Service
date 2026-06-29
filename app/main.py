from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import logging
from pathlib import Path

from app.config import settings
from app.routes.analytics import router as analytics_router, engine
from app.database import Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "ui" / "index.html"
LANDING_PATH = BASE_DIR / "ui" / "landing.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    # Tạo tất cả các bảng nếu chưa tồn tại
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.error(f"Could not create database tables: {e}")
        logger.warning("Service will start but database operations may fail.")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Analytics Service - Tong hop metrics tu nhieu service khac",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # fixed: True + "*" violates CORS spec
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics_router)


@app.get("/", tags=["root"])
async def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept or "application/xhtml+xml" in accept:
        return FileResponse(LANDING_PATH)

    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "ui": "/ui",
    }


@app.get("/ui", include_in_schema=False)
async def ui():
    return FileResponse(UI_PATH)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
