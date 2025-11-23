"""
Core utilities for Deep Vision
"""
import uuid
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime
import asyncio
from functools import wraps
import time


def generate_task_id() -> str:
    """Generate unique task ID"""
    return f"task_{uuid.uuid4().hex[:12]}"


def generate_file_hash(file_path: Path) -> str:
    """Generate SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in MB"""
    return file_path.stat().st_size / (1024 * 1024)


def get_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().isoformat()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove any path separators
    filename = filename.replace("/", "_").replace("\\", "_")
    # Remove any dangerous characters
    filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
    return filename


def retry_async(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
                    continue
            raise last_exception
        return wrapper
    return decorator


def measure_time(func):
    """Decorator to measure execution time"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


class ImageValidator:
    """Validate image files"""
    
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    MAX_FILE_SIZE_MB = 10
    
    @classmethod
    def validate_extension(cls, filename: str) -> bool:
        """Check if file extension is allowed"""
        ext = Path(filename).suffix.lower()
        return ext in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def validate_size(cls, file_size_bytes: int) -> bool:
        """Check if file size is within limit"""
        size_mb = file_size_bytes / (1024 * 1024)
        return size_mb <= cls.MAX_FILE_SIZE_MB
    
    @classmethod
    def validate_file(cls, filename: str, file_size: int) -> tuple[bool, Optional[str]]:
        """Validate file extension and size"""
        if not cls.validate_extension(filename):
            return False, f"File type not allowed. Allowed types: {', '.join(cls.ALLOWED_EXTENSIONS)}"
        
        if not cls.validate_size(file_size):
            return False, f"File size exceeds {cls.MAX_FILE_SIZE_MB}MB limit"
        
        return True, None
