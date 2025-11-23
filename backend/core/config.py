"""
Deep Vision - Multi-Agent Computer Vision System
Core configuration module
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "DeepVision"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8501,http://localhost:8000"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert ALLOWED_ORIGINS string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Image Model APIs
    REPLICATE_API_TOKEN: Optional[str] = None
    STABILITY_API_KEY: Optional[str] = None
    HUGGINGFACE_API_TOKEN: Optional[str] = None
    
    # Storage Paths
    UPLOAD_DIR: Path = Path("./uploads")
    OUTPUT_DIR: Path = Path("./outputs")
    MODEL_DIR: Path = Path("./models")
    CACHE_DIR: Path = Path("./cache")
    
    # GPU Settings
    CUDA_VISIBLE_DEVICES: str = "0"
    MAX_BATCH_SIZE: int = 1
    DEVICE: str = "cuda"  # or "cpu"
    ENABLE_XFORMERS: bool = False
    
    # Model Settings
    USE_LOCAL_MODELS: bool = False
    MAX_IMAGE_SIZE: int = 2048
    DEFAULT_IMAGE_SIZE: int = 512
    
    # Processing Settings
    MAX_CONCURRENT_TASKS: int = 3
    TASK_TIMEOUT: int = 300  # seconds
    CLEANUP_INTERVAL: int = 3600  # seconds
    
    # Database (Optional)
    DATABASE_URL: Optional[str] = None
    
    # Redis (Optional)
    REDIS_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
