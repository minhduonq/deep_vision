"""
Deep Vision - FastAPI Main Application
Multi-Agent Computer Vision System
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from loguru import logger
from typing import Optional
import aiofiles

from backend.core.config import settings
from backend.core.state import (
    TaskResponse, 
    TaskStatusResponse, 
    TaskResultResponse,
    EnhancementRequest,
    GenerationRequest
)
from backend.core.utils import (
    generate_task_id,
    sanitize_filename,
    ImageValidator
)
from backend.models.replicate_wrapper import replicate_client
import asyncio
import shutil

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    "logs/app_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

# In-memory task storage (TODO: replace with Redis/Database)
tasks_db: dict = {}


async def process_enhancement_task(task_id: str):
    """
    Background task to process image enhancement using Replicate API
    """
    try:
        task = tasks_db.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        logger.info(f"Starting processing for task {task_id}: {task.get('task_type', 'unknown')}")
        
        # Update status to processing
        tasks_db[task_id]["status"] = "processing"
        tasks_db[task_id]["progress"] = 10
        
        # Get input file path
        input_path = Path(task["file_path"])
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        tasks_db[task_id]["progress"] = 20
        
        # Process based on task type
        task_type = task.get("task_type", "deblur")
        output_path = None
        
        if task_type == "deblur":
            logger.info(f"Calling deblur model for task {task_id}")
            output_path = await replicate_client.deblur_image(input_path)
            
        elif task_type == "inpaint":
            logger.info(f"Calling inpaint model for task {task_id}")
            # For inpainting, we use LaMa which can auto-detect objects
            output_path = await replicate_client.inpaint_image(input_path)
            
        elif task_type == "beauty_enhance":
            logger.info(f"Calling beauty enhancement model for task {task_id}")
            output_path = await replicate_client.enhance_beauty(input_path)
            
        else:
            logger.warning(f"Unknown task type '{task_type}', using deblur")
            output_path = await replicate_client.deblur_image(input_path)
        
        tasks_db[task_id]["progress"] = 90
        
        if not output_path or not Path(output_path).exists():
            raise FileNotFoundError("Output file was not created")
        
        # Update task as completed
        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["result_path"] = str(output_path)
        tasks_db[task_id]["progress"] = 100
        
        logger.info(f"Task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)


async def process_generation_task(task_id: str):
    """
    Background task to process image generation
    TODO: Replace with actual agent implementation
    """
    try:
        task = tasks_db.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        logger.info(f"Starting generation for task {task_id}")
        
        # Update status
        tasks_db[task_id]["status"] = "processing"
        tasks_db[task_id]["progress"] = 20
        
        # Simulate processing
        await asyncio.sleep(3)
        tasks_db[task_id]["progress"] = 60
        
        # TODO: Implement actual generation
        # For now, return placeholder message
        
        await asyncio.sleep(2)
        tasks_db[task_id]["progress"] = 90
        
        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["progress"] = 100
        tasks_db[task_id]["message"] = "Generation feature will be implemented with agents"
        
        logger.info(f"Generation task {task_id} completed")
        
    except Exception as e:
        logger.error(f"Error in generation task {task_id}: {e}")
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Using device: {settings.DEVICE}")
    logger.info(f"Max concurrent tasks: {settings.MAX_CONCURRENT_TASKS}")
    
    # Ensure directories exist
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # TODO: Initialize agents and models
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    # TODO: Cleanup loaded models, close connections


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agent Computer Vision System for Image Enhancement and Generation",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving results
app.mount("/static", StaticFiles(directory=str(settings.OUTPUT_DIR)), name="static")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    gpu_available = False
    gpu_info = None
    
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        
        if gpu_available:
            gpu_info = {
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
                "device_name": torch.cuda.get_device_name(0),
                "memory_allocated_gb": round(torch.cuda.memory_allocated(0) / 1024**3, 2),
                "memory_reserved_gb": round(torch.cuda.memory_reserved(0) / 1024**3, 2),
            }
    except ImportError:
        logger.warning("PyTorch not installed, GPU info unavailable")
    except Exception as e:
        logger.error(f"Error checking GPU: {e}")
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "gpu_available": gpu_available,
        "gpu_info": gpu_info,
        "device": settings.DEVICE,
        "active_tasks": len([t for t in tasks_db.values() if t.get("status") == "processing"]),
        "total_tasks": len(tasks_db)
    }


@app.post("/api/v1/enhance", response_model=TaskResponse)
async def enhance_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    task_type: str = Form(...),
    description: Optional[str] = Form(None)
):
    """
    Endpoint for image enhancement tasks
    
    Supported task types:
    - deblur: Sharpen blurry images
    - inpaint: Remove objects from images
    - beauty_enhance: Enhance facial features
    """
    logger.info(f"Received enhancement request: {task_type}")
    
    # Validate file
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate task type
    valid_tasks = ["deblur", "inpaint", "beauty_enhance"]
    if task_type not in valid_tasks:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid task type. Must be one of: {', '.join(valid_tasks)}"
        )
    
    # Generate task ID
    task_id = generate_task_id()
    
    # Save uploaded file
    filename = sanitize_filename(file.filename or "upload.png")
    file_path = settings.UPLOAD_DIR / f"{task_id}_{filename}"
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"Saved file to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    # Create task entry
    task_entry = {
        "task_id": task_id,
        "status": "pending",
        "task_type": task_type,
        "description": description,
        "file_path": str(file_path),
        "progress": 0.0
    }
    tasks_db[task_id] = task_entry
    
    # Start processing in background
    background_tasks.add_task(process_enhancement_task, task_id)
    
    logger.info(f"Created task {task_id}")
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Enhancement task created successfully. Task type: {task_type}",
        estimated_time=30  # Estimate in seconds
    )


@app.post("/api/v1/generate", response_model=TaskResponse)
async def generate_image(
    background_tasks: BackgroundTasks,
    request: GenerationRequest
):
    """
    Endpoint for image generation from text prompts
    """
    logger.info(f"Received generation request: {request.prompt[:50]}...")
    
    # Generate task ID
    task_id = generate_task_id()
    
    # Create task entry
    task_entry = {
        "task_id": task_id,
        "status": "pending",
        "task_type": "generate",
        "prompt": request.prompt,
        "parameters": request.model_dump(),
        "progress": 0.0
    }
    tasks_db[task_id] = task_entry
    
    # Start processing in background
    background_tasks.add_task(process_generation_task, task_id)
    
    logger.info(f"Created generation task {task_id}")
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Image generation task created successfully",
        estimated_time=60
    )


@app.get("/api/v1/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get status of a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    result_url = None
    if task.get("status") == "completed" and "result_path" in task:
        # Generate URL for result
        result_path = Path(task["result_path"])
        result_url = f"/static/{result_path.name}"
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task.get("progress", 0.0),
        current_agent=task.get("current_agent"),
        error=task.get("error"),
        result_url=result_url
    )


@app.get("/api/v1/result/{task_id}")
async def get_task_result(task_id: str):
    """Get result of a completed task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Task not completed. Current status: {task['status']}"
        )
    
    if "result_path" not in task:
        raise HTTPException(status_code=404, detail="Result not found")
    
    result_path = Path(task["result_path"])
    
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        path=result_path,
        media_type="image/png",
        filename=result_path.name
    )


@app.delete("/api/v1/task/{task_id}")
async def delete_task(task_id: str):
    """Delete a task and its associated files"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    # Delete files
    if "file_path" in task:
        file_path = Path(task["file_path"])
        if file_path.exists():
            file_path.unlink()
    
    if "result_path" in task:
        result_path = Path(task["result_path"])
        if result_path.exists():
            result_path.unlink()
    
    # Remove from database
    del tasks_db[task_id]
    
    logger.info(f"Deleted task {task_id}")
    
    return {"message": "Task deleted successfully"}


@app.get("/api/v1/tasks")
async def list_tasks(status: Optional[str] = None, limit: int = 10):
    """List all tasks with optional status filter"""
    tasks = list(tasks_db.values())
    
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    
    # Sort by creation time (most recent first)
    tasks = sorted(tasks, key=lambda x: x["task_id"], reverse=True)
    
    # Limit results
    tasks = tasks[:limit]
    
    return {
        "total": len(tasks),
        "tasks": tasks
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": str(exc)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS
    )
