"""
AI Model Builder - FastAPI Backend
Main application entry point
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from api.routes import project, data, training, inference, export_routes, system, medical_routes, genomic_routes, ensemble_routes, comparison_routes, serving_routes, automl_routes, cloud_routes
from utils.config import settings
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown
    """
    # Startup
    logger.info("Starting AI Model Builder Backend...")
    
    # Create necessary directories
    projects_dir = Path("../projects")
    projects_dir.mkdir(exist_ok=True)
    
    logger.info("Backend initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Model Builder Backend...")

# Create FastAPI application with lifespan
app = FastAPI(
    title="AI Model Builder API",
    description="Backend API for Multi-Modal AI Training Application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(project.router, prefix="/api/project", tags=["Project Management"])
app.include_router(data.router, prefix="/api/data", tags=["Data Management"])
app.include_router(training.router, prefix="/api/training", tags=["Training"])
app.include_router(inference.router, prefix="/api/inference", tags=["Inference"])
app.include_router(export_routes.router, prefix="/api/export", tags=["Export"])
app.include_router(system.router, prefix="/api/system", tags=["System"])
app.include_router(medical_routes.router, tags=["Medical"])
app.include_router(genomic_routes.router, tags=["Genomic"])
app.include_router(ensemble_routes.router, tags=["Ensemble"])
app.include_router(comparison_routes.router, tags=["Comparison"])
app.include_router(serving_routes.router, tags=["Model Serving"])
app.include_router(automl_routes.router, tags=["AutoML"])
app.include_router(cloud_routes.router, tags=["Cloud Training"])

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "AI Model Builder API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "torch_available": True  # Will be checked dynamically
    }

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

