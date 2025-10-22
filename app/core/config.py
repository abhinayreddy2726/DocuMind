"""
Configuration settings for the application
"""
import os
import json
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    RELOAD: bool = Field(default=True)
    
    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="PAN & Aadhaar Extractor")
    VERSION: str = Field(default="1.0.0")
    
    # Moondream Configuration
    MOONDREAM_ENDPOINT: str = Field(default="http://localhost:2020/v1")
    MOONDREAM_MODEL: str = Field(default="moondream2")
    MOONDREAM_TIMEOUT: int = Field(default=30)
    
    # File Upload Settings
    UPLOAD_FOLDER: str = Field(default="uploads")
    OUTPUT_FOLDER: str = Field(default="outputs")
    LOGS_FOLDER: str = Field(default="logs")
    MAX_FILE_SIZE: int = Field(default=10485760)  # 10MB
    ALLOWED_EXTENSIONS: str = Field(default='["jpg", "jpeg", "png", "pdf"]')
    
    # Processing Settings
    SAVE_EXTRACTED_DATA: bool = Field(default=True)
    DELETE_UPLOADED_FILES: bool = Field(default=False)
    VALIDATE_PAN_FORMAT: bool = Field(default=True)
    VALIDATE_AADHAAR_FORMAT: bool = Field(default=True)
    
    # CORS Settings
    CORS_ORIGINS: str = Field(default='["http://localhost:3000", "http://localhost:8000"]')
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: str = Field(default='["*"]')
    CORS_ALLOW_HEADERS: str = Field(default='["*"]')
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=False)
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_PERIOD: int = Field(default=60)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_allowed_extensions(self) -> List[str]:
        """Parse allowed extensions from JSON string"""
        try:
            return json.loads(self.ALLOWED_EXTENSIONS)
        except:
            return ["jpg", "jpeg", "png", "pdf"]
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from JSON string"""
        try:
            return json.loads(self.CORS_ORIGINS)
        except:
            return ["*"]
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for folder in [self.UPLOAD_FOLDER, self.OUTPUT_FOLDER, self.LOGS_FOLDER]:
            Path(folder).mkdir(parents=True, exist_ok=True)
            # Create .gitkeep file
            gitkeep = Path(folder) / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()


# Create global settings instance
settings = Settings()

# Ensure directories exist
settings.ensure_directories()

