"""
Configuration management for the backend
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8181
    DEBUG: bool = True
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    PROJECTS_DIR: Path = BASE_DIR.parent / "projects"
    MODELS_DIR: Path = BASE_DIR / "models"
    TEMP_DIR: Path = BASE_DIR / "temp"
    
    # Training settings
    MAX_WORKERS: int = 4
    DEFAULT_DEVICE: str = "cuda"  # Will fallback to CPU if CUDA unavailable
    
    # File upload limits
    MAX_UPLOAD_SIZE: int = 1024 * 1024 * 1024  # 1GB
    CHUNK_SIZE: int = 1024 * 1024  # 1MB chunks
    
    # Cloud training settings (for future use)
    CLOUD_PROVIDER: Optional[str] = None
    CLOUD_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Ensure directories exist
settings.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)

