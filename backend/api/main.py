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
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks, Depends, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
from backend.agents.huggingface_generation_agent import generation_agent
from backend.agents.nano_banana_agent import nano_banana_agent
from backend.agents.imagen4_agent import imagen4_agent
from backend.agents.qwen_fast_edit_agent import qwen_fast_edit_agent
from backend.agents.qwen_lora_fusion_agent import qwen_lora_fusion_agent
from backend.auth.auth_routes import router as auth_router
from backend.auth.jwt import decode_token
from backend.api.chat_routes import router as chat_router
from backend.api.chat_agent_routes import router as chat_agent_router
from backend.api.history_routes import router as history_router
from backend.database.database import init_db, get_db
from backend.database import crud
from backend.core.history_helper import save_task_with_chat, update_task_result
from sqlalchemy.orm import Session
import asyncio
import shutil
import uuid

security = HTTPBearer(auto_error=False)

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


# ==================== HELPER FUNCTIONS ====================

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user from token if provided, otherwise return None"""
    if not credentials:
        return None
    
    try:
        payload = decode_token(credentials.credentials)
        if not payload:
            return None
        
        username = payload.get("sub")
        if not username:
            return None
        
        user = crud.get_user_by_username(db, username)
        return user
    except Exception as e:
        logger.warning(f"Failed to get optional user: {e}")
        return None


def save_chat_message(
    db: Session,
    user_id: int,
    session_id: str,
    role: str,
    message: str,
    extra_data: dict = None
):
    """Helper function to save chat message to database"""
    try:
        crud.create_chat_message(
            db=db,
            user_id=user_id,
            session_id=session_id,
            role=role,
            message=message,
            extra_data=extra_data
        )
        logger.debug(f"Saved chat message for user {user_id}, session {session_id}")
    except Exception as e:
        logger.error(f"Failed to save chat message: {e}")


def save_task_to_history(
    db: Session,
    user_id: int,
    task_id: str,
    task_type: str,
    prompt: str = None,
    parameters: dict = None
):
    """Helper function to save task to database"""
    try:
        crud.create_task(
            db=db,
            user_id=user_id,
            task_id=task_id,
            task_type=task_type,
            prompt=prompt,
            parameters=parameters
        )
        logger.debug(f"Saved task {task_id} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to save task: {e}")


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


async def process_generation_task(task_id: str, user_id: Optional[int] = None):
    """
    Background task to process image generation using HuggingFace API
    """
    from backend.database.database import SessionLocal
    
    try:
        task = tasks_db.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        logger.info(f"Starting generation for task {task_id}")
        
        # Update status
        tasks_db[task_id]["status"] = "processing"
        tasks_db[task_id]["progress"] = 10
        
        # Get task details
        prompt = task.get("prompt", "A beautiful landscape")
        width = task.get("width", 512)
        height = task.get("height", 512)
        steps = task.get("steps", 8)  # FLUX.1-schnell max is 16
        guidance = task.get("guidance", 3.5)  # FLUX works better with lower guidance
        
        tasks_db[task_id]["progress"] = 30
        logger.info(f"Generating image with prompt: '{prompt[:50]}...'")
        
        # Generate output path
        output_filename = f"generated_{task_id}.png"
        output_path = settings.OUTPUT_DIR / output_filename
        
        tasks_db[task_id]["progress"] = 40
        
        # Map width/height to resolution
        resolution = "square"  # default
        if width == height:
            resolution = "square"  # 1024x1024
        elif width < height:
            resolution = "portrait"  # 768x1024
        elif width > height:
            if width / height > 1.5:
                resolution = "wide"  # 1280x720 or 1920x1080
            else:
                resolution = "landscape"  # 1024x768
        
        # Try HuggingFace first, fallback to Nano Banana if quota exceeded
        result = None
        error_message = None
        
        try:
            # Call HuggingFace generation agent
            logger.info("Trying HuggingFace Z-Image-Turbo...")
            result = await generation_agent.generate_image(
                prompt=prompt,
                resolution=resolution,
                steps=steps,
                shift=guidance,
                random_seed=True
            )
            
            if not result.get("success"):
                error_message = result.get("error", "")
                raise Exception(error_message)
                
        except Exception as hf_error:
            error_str = str(hf_error)
            logger.warning(f"HuggingFace generation failed: {error_str}")
            
            # Check if it's a quota error
            if "quota" in error_str.lower() or "exceeded" in error_str.lower() or "runtime" in error_str.lower():
                logger.info("🔄 HuggingFace quota exceeded, falling back to Imagen 4 (Replicate)...")
                tasks_db[task_id]["current_agent"] = "Imagen 4 (Google)"
                tasks_db[task_id]["progress"] = 45
                
                #Fallback to Imagen 4
                try:
                    result = await imagen4_agent.generate_image(
                        prompt=prompt,
                        width=width,
                        height=height,
                        negative_prompt="",
                        output_format="png",
                        output_quality=90
                    )
                    
                    if not result.get("success"):
                        raise Exception(result.get("error", "Imagen 4 generation failed"))
                        
                    logger.success("✅ Successfully generated with Imagen 4 fallback")
                    
                except Exception as img4_error:
                    logger.error(f"❌ Imagen 4 fallback also failed: {img4_error}")
                    raise Exception(f"Both generation methods failed. HF: {error_str}, Imagen4: {str(img4_error)}")
            else:
                # Not a quota error, raise original error
                raise
        
        tasks_db[task_id]["progress"] = 90
        
        if result.get("success"):
            # Save the generated image to output directory
            generated_path = result.get("output_path")
            
            # Handle if generated_path is still a list/tuple
            if isinstance(generated_path, (list, tuple)):
                generated_path = generated_path[0] if generated_path else None
            
            # Convert Replicate FileOutput to string
            if hasattr(generated_path, 'url'):
                generated_path = str(generated_path.url)
            elif not isinstance(generated_path, str):
                generated_path = str(generated_path)
            
            logger.info(f"Generated path: {generated_path}, type: {type(generated_path)}")
            
            # Check if it's a URL (from Replicate) or local path (from HuggingFace)
            is_url = isinstance(generated_path, str) and generated_path.startswith(('http://', 'https://'))
            
            if is_url:
                # Download from URL
                logger.info(f"Downloading image from URL: {generated_path}")
                import httpx
                
                output_filename = f"generated_{task_id}.png"
                final_output_path = settings.OUTPUT_DIR / output_filename
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(generated_path)
                    response.raise_for_status()
                    
                    with open(final_output_path, 'wb') as f:
                        f.write(response.content)
                
                logger.success(f"Downloaded image to: {final_output_path}")
                
            elif generated_path and Path(generated_path).exists():
                # Copy local file
                output_filename = f"generated_{task_id}.png"
                final_output_path = settings.OUTPUT_DIR / output_filename
                shutil.copy(generated_path, final_output_path)
                
                logger.success(f"Copied image to: {final_output_path}")
            else:
                error_msg = f"Generated image not found or path invalid: {generated_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            tasks_db[task_id]["status"] = "completed"
            tasks_db[task_id]["progress"] = 100
            tasks_db[task_id]["output_path"] = str(final_output_path)
            tasks_db[task_id]["result_path"] = str(final_output_path)
            tasks_db[task_id]["result_url"] = f"/static/{output_filename}"
            tasks_db[task_id]["metadata"] = result.get("metadata", {})
            tasks_db[task_id]["message"] = "Image generated successfully"
            logger.info(f"✅ Generation task {task_id} completed")
            
            # Update database if user is authenticated
            if user_id:
                db = SessionLocal()
                try:
                    session_id = task.get("session_id")
                    update_task_result(
                        db=db,
                        user_id=user_id,
                        task_id=task_id,
                        session_id=session_id,
                        status="completed",
                        result_path=f"/static/{output_filename}"
                    )
                    logger.info(f"Updated task result in database for user {user_id}")
                except Exception as db_error:
                    logger.error(f"Failed to update task in database: {db_error}")
                finally:
                    db.close()
        else:
            tasks_db[task_id]["status"] = "failed"
            tasks_db[task_id]["error"] = result.get("error", "Unknown error")
            logger.error(f"❌ Generation task {task_id} failed: {result.get('error')}")
            
            # Update database if user is authenticated
            if user_id:
                db = SessionLocal()
                try:
                    session_id = task.get("session_id")
                    update_task_result(
                        db=db,
                        user_id=user_id,
                        task_id=task_id,
                        session_id=session_id,
                        status="failed",
                        error_message=result.get("error", "Unknown error")
                    )
                except Exception as db_error:
                    logger.error(f"Failed to update task in database: {db_error}")
                finally:
                    db.close()
        
    except Exception as e:
        logger.error(f"Error in generation task {task_id}: {e}")
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)
        
        # Update database if user is authenticated
        if user_id:
            db = SessionLocal()
            try:
                session_id = task.get("session_id")
                update_task_result(
                    db=db,
                    user_id=user_id,
                    task_id=task_id,
                    session_id=session_id,
                    status="failed",
                    error_message=str(e)
                )
            except Exception as db_error:
                logger.error(f"Failed to update task in database: {db_error}")
            finally:
                db.close()


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
    
    # Initialize database
    try:
        init_db()
        logger.success("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
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

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(chat_agent_router)
app.include_router(history_router)

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
    request: GenerationRequest,
    current_user = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint for image generation from text prompts using HuggingFace API
    
    Parameters:
    - prompt: Text description of the image to generate
    - width: Image width (default: 512)
    - height: Image height (default: 512)
    - steps: Number of inference steps (default: 30)
    - guidance: Guidance scale (default: 7.5)
    """
    logger.info(f"Received generation request: {request.prompt[:50]}... (User: {current_user.username if current_user else 'Anonymous'})")
    
    # Generate task ID
    task_id = generate_task_id()
    
    # Save to database if user is authenticated
    session_id = None
    if current_user:
        try:
            session_id = save_task_with_chat(
                db=db,
                user_id=current_user.id,
                task_id=task_id,
                task_type="generate",
                prompt=request.prompt,
                parameters={
                    "width": getattr(request, 'width', 512),
                    "height": getattr(request, 'height', 512),
                    "steps": getattr(request, 'steps', 30),
                    "guidance": getattr(request, 'guidance', 7.5)
                }
            )
            logger.info(f"Saved generation task to database for user {current_user.username}")
        except Exception as e:
            logger.error(f"Failed to save task to database: {e}")
    
    # Create task entry with all parameters
    task_entry = {
        "task_id": task_id,
        "status": "pending",
        "task_type": "generate",
        "prompt": request.prompt,
        "width": getattr(request, 'width', 512),
        "height": getattr(request, 'height', 512),
        "steps": getattr(request, 'steps', 30),
        "guidance": getattr(request, 'guidance', 7.5),
        "progress": 0,
        "user_id": current_user.id if current_user else None,
        "session_id": session_id
    }
    tasks_db[task_id] = task_entry
    
    # Start processing in background
    background_tasks.add_task(process_generation_task, task_id, current_user.id if current_user else None)
    
    logger.info(f"Created generation task {task_id}")
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Image generation task created. This may take 30-60 seconds.",
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
        logger.info(f"Task {task_id} completed. Result URL: {result_url}, Path: {result_path}")
    
    response = TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task.get("progress", 0.0),
        current_agent=task.get("current_agent"),
        error=task.get("error"),
        result_url=result_url
    )
    
    logger.debug(f"Returning status for {task_id}: {response}")
    return response


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


# ============================================================================
# QWEN EDIT ENDPOINTS - Fast single image editing
# ============================================================================

@app.post("/api/v1/edit/fast", response_model=TaskResponse)
async def fast_edit_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    prompt: str = Form(...),
    guidance_scale: float = Form(1.0),
    steps: int = Form(8)
):
    """
    Fast single image editing with Qwen
    
    Use cases: color changes, style transfer, simple modifications
    """
    logger.info(f"Received fast edit request: {prompt}")
    
    # Validate file
    content = await file.read()
    is_valid, error_msg = ImageValidator.validate_file(file.filename, len(content))
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    task_id = generate_task_id()
    safe_filename = sanitize_filename(file.filename)
    file_path = settings.UPLOAD_DIR / f"{task_id}_{safe_filename}"
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Create task
    task_entry = {
        "task_id": task_id,
        "status": "pending",
        "task_type": "fast_edit",
        "file_path": str(file_path),
        "prompt": prompt,
        "guidance_scale": guidance_scale,
        "steps": steps,
        "progress": 0
    }
    tasks_db[task_id] = task_entry
    
    # Process in background
    background_tasks.add_task(process_fast_edit_task, task_id)
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Fast edit task created",
        estimated_time=15
    )


@app.post("/api/v1/edit/fusion", response_model=TaskResponse)
async def fusion_edit_images(
    background_tasks: BackgroundTasks,
    image_1: UploadFile = File(...),
    image_2: UploadFile = File(...),
    prompt: str = Form(...),
    lora_adapter: str = Form("Super-Fusion"),
    guidance_scale: float = Form(1.0),
    steps: int = Form(4)
):
    """
    Multi-image fusion editing with LoRA styles
    
    Use cases: object replacement, style fusion, fashion transfer
    """
    logger.info(f"Received fusion edit request: {prompt}")
    
    # Validate and read files
    content1 = await image_1.read()
    content2 = await image_2.read()
    
    is_valid1, error_msg1 = ImageValidator.validate_file(image_1.filename, len(content1))
    if not is_valid1:
        raise HTTPException(status_code=400, detail=f"Image 1: {error_msg1}")
    
    is_valid2, error_msg2 = ImageValidator.validate_file(image_2.filename, len(content2))
    if not is_valid2:
        raise HTTPException(status_code=400, detail=f"Image 2: {error_msg2}")
    
    task_id = generate_task_id()
    
    # Save both images
    file1_path = settings.UPLOAD_DIR / f"{task_id}_1_{sanitize_filename(image_1.filename)}"
    file2_path = settings.UPLOAD_DIR / f"{task_id}_2_{sanitize_filename(image_2.filename)}"
    
    async with aiofiles.open(file1_path, 'wb') as f:
        await f.write(content1)
    
    async with aiofiles.open(file2_path, 'wb') as f:
        await f.write(content2)
    
    # Create task
    task_entry = {
        "task_id": task_id,
        "status": "pending",
        "task_type": "fusion_edit",
        "file_path_1": str(file1_path),
        "file_path_2": str(file2_path),
        "prompt": prompt,
        "lora_adapter": lora_adapter,
        "guidance_scale": guidance_scale,
        "steps": steps,
        "progress": 0
    }
    tasks_db[task_id] = task_entry
    
    # Process in background
    background_tasks.add_task(process_fusion_edit_task, task_id)
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Fusion edit task created",
        estimated_time=20
    )


@app.get("/api/v1/edit/lora-styles")
async def list_lora_styles():
    """Get available LoRA style adapters"""
    styles = qwen_lora_fusion_agent.list_lora_adapters()
    return {
        "styles": [
            {"name": name, "description": desc}
            for name, desc in styles.items()
        ]
    }


# Background task processors for new endpoints
async def process_fast_edit_task(task_id: str):
    """Process fast edit task"""
    try:
        task = tasks_db[task_id]
        tasks_db[task_id]["status"] = "processing"
        tasks_db[task_id]["progress"] = 20
        
        result = await qwen_fast_edit_agent.edit_image(
            image_path=task["file_path"],
            prompt=task["prompt"],
            guidance_scale=task["guidance_scale"],
            num_inference_steps=task["steps"]
        )
        
        if result["success"]:
            # Copy result from temp to outputs directory
            temp_path = Path(result["output_path"])
            output_filename = f"{task_id}_result{temp_path.suffix}"
            output_path = settings.OUTPUT_DIR / output_filename
            
            # Copy file
            shutil.copy2(temp_path, output_path)
            
            tasks_db[task_id]["status"] = "completed"
            tasks_db[task_id]["progress"] = 100
            tasks_db[task_id]["result_path"] = str(output_path)
            logger.success(f"Fast edit completed for task {task_id}, saved to {output_path}")
        else:
            tasks_db[task_id]["status"] = "failed"
            tasks_db[task_id]["error"] = result["error"]
            logger.error(f"Fast edit failed for task {task_id}: {result['error']}")
            
    except Exception as e:
        logger.error(f"Error in fast edit task {task_id}: {e}")
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)


async def process_fusion_edit_task(task_id: str):
    """Process fusion edit task"""
    try:
        task = tasks_db[task_id]
        tasks_db[task_id]["status"] = "processing"
        tasks_db[task_id]["progress"] = 20
        
        result = await qwen_lora_fusion_agent.edit_with_fusion(
            image_1=task["file_path_1"],
            image_2=task["file_path_2"],
            prompt=task["prompt"],
            lora_adapter=task["lora_adapter"],
            guidance_scale=task["guidance_scale"],
            steps=task["steps"]
        )
        
        if result["success"]:
            # Copy result from temp to outputs directory
            temp_path = Path(result["output_path"])
            output_filename = f"{task_id}_result{temp_path.suffix}"
            output_path = settings.OUTPUT_DIR / output_filename
            
            # Copy file
            shutil.copy2(temp_path, output_path)
            
            tasks_db[task_id]["status"] = "completed"
            tasks_db[task_id]["progress"] = 100
            tasks_db[task_id]["result_path"] = str(output_path)
            logger.success(f"Fusion edit completed for task {task_id}, saved to {output_path}")
        else:
            tasks_db[task_id]["status"] = "failed"
            tasks_db[task_id]["error"] = result["error"]
            logger.error(f"Fusion edit failed for task {task_id}: {result['error']}")
            
    except Exception as e:
        logger.error(f"Error in fusion edit task {task_id}: {e}")
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)


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
