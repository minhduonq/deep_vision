"""
Chat Agent Routes - Continuous conversation with AI agents
Orchestrator automatically routes requests to appropriate agents
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from loguru import logger
import uuid
import aiofiles
import shutil
import httpx
from pathlib import Path

from backend.database.database import get_db
from backend.database import crud
from backend.auth.jwt import decode_token
from backend.core.config import settings
from backend.core.utils import generate_task_id, sanitize_filename
from backend.core.history_helper import save_task_with_chat, update_task_result, get_or_create_session
from backend.agents.imagen4_agent import imagen4_agent
from backend.agents.huggingface_generation_agent import generation_agent
from backend.models.replicate_wrapper import replicate_client
from backend.agents.qwen_fast_edit_agent import qwen_fast_edit_agent
from backend.agents.nano_banana_agent import nano_banana_agent

router = APIRouter(prefix="/api/v1/chat-agent", tags=["chat-agent"])
security = HTTPBearer()


# ==================== SCHEMAS ====================

class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Can you enhance this image and make it brighter?",
                "session_id": "session_abc123"
            }
        }


class ChatResponse(BaseModel):
    """Schema for chat response"""
    message: str
    session_id: str
    task_id: Optional[str] = None
    task_type: Optional[str] = None
    requires_image: bool = False
    status: str  # 'waiting_input', 'processing', 'completed'
    result_url: Optional[str] = None
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I'll create that image for you...",
                "session_id": "session_abc123",
                "task_id": "task_xyz",
                "status": "processing",
                "timestamp": "2025-12-10T08:00:00"
            }
        }


class AgentAction(BaseModel):
    """Schema for agent action"""
    agent_name: str
    action: str
    parameters: Optional[dict] = None


# ==================== DEPENDENCIES ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = crud.get_user_by_username(db, username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


# ==================== AGENT ORCHESTRATOR ====================

class ChatOrchestrator:
    """
    Intelligent orchestrator that analyzes user messages
    and routes to appropriate agents
    """
    
    @staticmethod
    def analyze_intent(message: str) -> dict:
        """
        Analyze user message to determine intent and required agent
        
        Returns:
            dict with 'intent', 'agent', 'requires_image', 'action'
        """
        message_lower = message.lower()
        
        # Image generation keywords
        generation_keywords = ['generate', 'create', 'make', 'draw', 'tạo', 'vẽ', 'sinh']
        if any(keyword in message_lower for keyword in generation_keywords):
            if 'image' in message_lower or 'picture' in message_lower or 'ảnh' in message_lower or 'hình' in message_lower:
                return {
                    'intent': 'generate_image',
                    'agent': 'generation_agent',
                    'requires_image': False,
                    'action': 'generate',
                    'prompt': message
                }
        
        # Edit keywords (check first, more specific)
        edit_keywords = ['edit', 'change', 'modify', 'adjust', 'transform', 'convert', 
                        'chỉnh sửa', 'thay đổi', 'điều chỉnh', 'biến đổi', 'chuyển đổi']
        edit_indicators = ['make it', 'turn into', 'change to', 'transform to', 
                          'thành', 'sang', 'làm cho']
        if (any(keyword in message_lower for keyword in edit_keywords) or 
            any(indicator in message_lower for indicator in edit_indicators)):
            # If it mentions specific changes (colors, objects, style), it's editing
            if any(word in message_lower for word in ['color', 'style', 'background', 'màu', 'nền', 'phong cách']):
                return {
                    'intent': 'edit_image',
                    'agent': 'qwen_edit_agent',
                    'requires_image': True,
                    'action': 'edit',
                    'prompt': message
                }
        
        # Deblur keywords (more specific)
        blur_keywords = ['blur', 'blurry', 'sharp', 'focus', 'clarity', 
                        'mờ', 'nét', 'rõ', 'sắc nét', 'làm nét']
        if any(keyword in message_lower for keyword in blur_keywords):
            return {
                'intent': 'deblur_image',
                'agent': 'enhancement_agent',
                'requires_image': True,
                'action': 'deblur'
            }
        
        # Inpaint/remove keywords
        remove_keywords = ['remove', 'delete', 'erase', 'clean', 'clear', 'eliminate',
                          'xóa', 'loại bỏ', 'xoá', 'bỏ', 'gỡ']
        if any(keyword in message_lower for keyword in remove_keywords):
            return {
                'intent': 'remove_object',
                'agent': 'enhancement_agent',
                'requires_image': True,
                'action': 'inpaint'
            }
        
        # General enhancement keywords (less specific, check last)
        enhancement_keywords = ['enhance', 'improve', 'fix', 'repair', 'restore', 'beautify', 'quality',
                               'cải thiện', 'tăng cường', 'sửa', 'nâng cao', 'làm đẹp', 'chất lượng']
        if any(keyword in message_lower for keyword in enhancement_keywords):
            return {
                'intent': 'enhance_image',
                'agent': 'enhancement_agent',
                'requires_image': True,
                'action': 'enhance'
            }
        
        # Default: conversational
        return {
            'intent': 'conversation',
            'agent': None,
            'requires_image': False,
            'action': 'chat'
        }
    
    @staticmethod
    def generate_response(intent_data: dict, has_image: bool = False) -> str:
        """Generate appropriate response based on intent"""
        
        intent = intent_data['intent']
        requires_image = intent_data.get('requires_image', False)
        
        if intent == 'generate_image':
            return "🎨 Tôi sẽ tạo hình ảnh theo yêu cầu của bạn. Đang xử lý, vui lòng đợi một chút..."
        
        elif intent == 'enhance_image':
            if not has_image:
                return "📸 Vui lòng tải lên hình ảnh bạn muốn cải thiện. Bạn có thể kéo thả hoặc nhấn nút 📎 để tải ảnh lên."
            return "✨ Tôi sẽ cải thiện chất lượng hình ảnh của bạn. Đang xử lý..."
        
        elif intent == 'deblur_image':
            if not has_image:
                return "📸 Vui lòng tải lên hình ảnh bị mờ để tôi có thể làm nét lại. Nhấn vào biểu tượng 📎 để tải ảnh."
            return "🔍 Tôi sẽ làm nét hình ảnh của bạn. Đang xử lý..."
        
        elif intent == 'remove_object':
            if not has_image:
                return "📸 Vui lòng tải lên hình ảnh chứa đối tượng bạn muốn xóa. Nhấn vào 📎 để tải ảnh."
            return "🧹 Tôi sẽ loại bỏ đối tượng không mong muốn khỏi hình ảnh. Đang xử lý..."
        
        elif intent == 'edit_image':
            if not has_image:
                return "📸 Vui lòng tải lên hình ảnh bạn muốn chỉnh sửa. Nhấn vào biểu tượng 📎 để tải ảnh lên."
            return "🎨 Tôi sẽ chỉnh sửa hình ảnh theo yêu cầu của bạn. Đang xử lý với AI..."
        
        else:
            return """👋 Xin chào! Tôi là trợ lý AI của Deep Vision. Tôi có thể giúp bạn:

• 🎨 **Tạo hình ảnh** từ mô tả văn bản (không cần ảnh gốc)
• ✨ **Cải thiện chất lượng** hình ảnh (tải ảnh + mô tả)
• 🔍 **Làm nét** hình ảnh bị mờ (tải ảnh lên)
• 🧹 **Xóa đối tượng** không mong muốn (tải ảnh + mô tả)
• 🎨 **Chỉnh sửa** hình ảnh theo prompt (tải ảnh + mô tả thay đổi)

Hãy cho tôi biết bạn muốn làm gì! Đừng quên tải ảnh lên bằng nút 📎 nếu cần."""


# ==================== BACKGROUND TASK PROCESSING ====================

# In-memory task storage (similar to main.py)
chat_tasks_db = {}

async def process_enhancement_task(
    task_id: str,
    task_type: str,
    image_path: str,
    prompt: Optional[str],
    user_id: int,
    session_id: str
):
    """Background task to process image enhancement/editing"""
    from backend.database.database import SessionLocal
    db = SessionLocal()
    
    try:
        chat_tasks_db[task_id] = {
            "status": "processing",
            "progress": 10,
            "current_agent": task_type
        }
        
        logger.info(f"Starting enhancement task {task_id}: {task_type}")
        
        input_path = Path(image_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        chat_tasks_db[task_id]["progress"] = 30
        
        # Process based on task type
        output_path = None
        
        if task_type == "deblur":
            logger.info(f"Deblurring image for task {task_id}")
            output_path = await replicate_client.deblur_image(input_path)
            
        elif task_type == "inpaint":
            logger.info(f"Inpainting image for task {task_id}")
            output_path = await replicate_client.inpaint_image(input_path)
            
        elif task_type == "enhance":
            logger.info(f"Enhancing image for task {task_id}")
            output_path = await replicate_client.enhance_beauty(input_path)
            
        elif task_type == "edit":
            logger.info(f"Editing image with Qwen for task {task_id}")
            if not prompt:
                raise ValueError("Prompt required for image editing")
            
            # Use Qwen Fast Edit Agent
            # result = await qwen_fast_edit_agent.edit_image(
            #     image_path=str(input_path),
            #     prompt=prompt
            # )

            # Use Nano Banana Edit Agent
            result = await nano_banana_agent.process_edit_request(
                image_path=str(input_path),
                prompt=prompt,
                output_dir=str(settings.OUTPUT_DIR)
            )
            
            if result.get("success"):
                output_path = result.get("output_path")
            else:
                raise Exception(result.get("error", "Qwen edit failed"))
        else:
            raise ValueError(f"Unknown task type: {task_type}")
        
        chat_tasks_db[task_id]["progress"] = 80
        
        if not output_path or not Path(output_path).exists():
            raise FileNotFoundError("Output file was not created")
        
        # Save result to outputs directory
        output_filename = f"enhanced_{task_id}.png"
        final_output_path = settings.OUTPUT_DIR / output_filename
        shutil.copy(output_path, final_output_path)
        
        result_url = f"/outputs/{output_filename}"
        
        # Update task in database
        update_task_result(
            db=db,
            user_id=user_id,
            task_id=task_id,
            session_id=session_id,
            status="completed",
            result_path=result_url
        )
        
        chat_tasks_db[task_id] = {
            "status": "completed",
            "progress": 100,
            "result_url": result_url
        }
        
        # Add completion message to chat
        crud.create_chat_message(
            db=db,
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            message="✅ Đã hoàn thành! Đây là kết quả:",
            extra_data={
                "task_id": task_id,
                "result_url": result_url
            }
        )
        
        logger.success(f"Enhancement task {task_id} completed successfully")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing enhancement task {task_id}: {error_msg}")
        chat_tasks_db[task_id] = {
            "status": "failed",
            "error": error_msg
        }
        update_task_result(
            db=db,
            user_id=user_id,
            task_id=task_id,
            session_id=session_id,
            status="failed",
            error_message=error_msg
        )
    finally:
        db.close()


async def process_generation_task(
    task_id: str,
    prompt: str,
    user_id: int,
    session_id: str
):
    """Background task to process image generation"""
    # Create new DB session for background task
    from backend.database.database import SessionLocal
    db = SessionLocal()
    
    try:
        chat_tasks_db[task_id] = {
            "status": "processing",
            "progress": 10,
            "current_agent": "Imagen 4"
        }
        
        logger.info(f"Starting generation task {task_id}")
        
        # Try Imagen 4 first
        result = await imagen4_agent.generate_image(
            prompt=prompt,
            width=1024,
            height=1024,
            output_format="png",
            output_quality=90
        )
        
        chat_tasks_db[task_id]["progress"] = 80
        
        if result.get("success"):
            generated_path = result.get("output_path")
            
            # Handle Replicate URL
            if isinstance(generated_path, str) and generated_path.startswith(('http://', 'https://')):
                logger.info(f"Downloading image from URL: {generated_path}")
                
                output_filename = f"generated_{task_id}.png"
                final_output_path = settings.OUTPUT_DIR / output_filename
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(generated_path)
                    response.raise_for_status()
                    
                    with open(final_output_path, 'wb') as f:
                        f.write(response.content)
                
                result_url = f"/outputs/{output_filename}"
            else:
                result_url = generated_path
            
            # Update task in database
            update_task_result(
                db=db,
                user_id=user_id,
                task_id=task_id,
                session_id=session_id,
                status="completed",
                result_path=result_url
            )
            
            chat_tasks_db[task_id] = {
                "status": "completed",
                "progress": 100,
                "result_url": result_url
            }
            
            # Add completion message to chat
            crud.create_chat_message(
                db=db,
                user_id=user_id,
                session_id=session_id,
                role="assistant",
                message="✅ Đã hoàn thành! Đây là kết quả:",
                extra_data={
                    "task_id": task_id,
                    "result_url": result_url
                }
            )
            
            logger.success(f"Task {task_id} completed successfully")
        else:
            error_msg = result.get("error", "Generation failed")
            chat_tasks_db[task_id] = {
                "status": "failed",
                "error": error_msg
            }
            update_task_result(
                db=db,
                user_id=user_id,
                task_id=task_id,
                session_id=session_id,
                status="failed",
                error_message=error_msg
            )
            logger.error(f"Task {task_id} failed: {error_msg}")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing task {task_id}: {error_msg}")
        chat_tasks_db[task_id] = {
            "status": "failed",
            "error": error_msg
        }
        update_task_result(
            db=db,
            user_id=user_id,
            task_id=task_id,
            session_id=session_id,
            status="failed",
            error_message=error_msg
        )
    finally:
        # Close DB session
        db.close()


# ==================== ENDPOINTS ====================

@router.post("/message", response_model=ChatResponse)
async def send_message(
    message: str = Form(...),
    session_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the chat agent
    Agent automatically determines the appropriate action
    """
    try:
        # Get or create session
        session_id = get_or_create_session(db, current_user.id, session_id)
        
        # Check if this is the first message in session (to set title)
        existing_messages = crud.get_chat_history(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            limit=1
        )
        
        is_first_message = len(existing_messages) == 0
        
        # Create or update chat session with title from first user message
        if is_first_message:
            # Extract title from message (first 100 chars)
            title = message[:100] if len(message) <= 100 else message[:97] + "..."
            crud.create_or_update_chat_session(
                db=db,
                user_id=current_user.id,
                session_id=session_id,
                title=title,
                task_type="chat"
            )
        
        # Save user message
        crud.create_chat_message(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            role="user",
            message=message,
            extra_data={"has_image": image is not None}
        )
        
        # Analyze intent
        intent_data = ChatOrchestrator.analyze_intent(message)
        logger.info(f"User intent: {intent_data['intent']}, Agent: {intent_data.get('agent')}")
        
        # Check if image is required but not provided
        if intent_data.get('requires_image') and not image:
            response_message = ChatOrchestrator.generate_response(intent_data, has_image=False)
            
            # Save assistant response
            crud.create_chat_message(
                db=db,
                user_id=current_user.id,
                session_id=session_id,
                role="assistant",
                message=response_message,
                extra_data={"intent": intent_data}
            )
            
            return ChatResponse(
                message=response_message,
                session_id=session_id,
                status="waiting_input",
                requires_image=True,
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Generate response
        response_message = ChatOrchestrator.generate_response(intent_data, has_image=image is not None)
        
        # If this is a task that requires processing
        if intent_data.get('agent'):
            task_id = generate_task_id()
            
            # Save image if provided
            image_path = None
            if image:
                filename = sanitize_filename(image.filename or "upload.png")
                file_path = settings.UPLOAD_DIR / f"{task_id}_{filename}"
                
                async with aiofiles.open(file_path, 'wb') as f:
                    content = await image.read()
                    await f.write(content)
                
                image_path = str(file_path)
                logger.info(f"Saved image to {file_path}")
            
            # Save task with chat
            save_task_with_chat(
                db=db,
                user_id=current_user.id,
                task_id=task_id,
                task_type=intent_data['action'],
                prompt=intent_data.get('prompt', message),
                parameters={
                    'intent': intent_data['intent'],
                    'image_path': image_path
                },
                session_id=session_id
            )
            
            # Save assistant response
            crud.create_chat_message(
                db=db,
                user_id=current_user.id,
                session_id=session_id,
                role="assistant",
                message=response_message,
                extra_data={
                    "task_id": task_id,
                    "task_type": intent_data['action'],
                    "intent": intent_data
                }
            )
            
            # Start background processing based on intent
            if intent_data['intent'] == 'generate_image':
                background_tasks.add_task(
                    process_generation_task,
                    task_id=task_id,
                    prompt=intent_data.get('prompt', message),
                    user_id=current_user.id,
                    session_id=session_id
                )
            elif intent_data['intent'] in ['enhance_image', 'deblur_image', 'remove_object', 'edit_image']:
                # For enhancement/editing tasks
                if not image_path:
                    raise HTTPException(
                        status_code=400,
                        detail="Image is required for enhancement/editing tasks"
                    )
                
                background_tasks.add_task(
                    process_enhancement_task,
                    task_id=task_id,
                    task_type=intent_data['action'],
                    image_path=image_path,
                    prompt=intent_data.get('prompt', message) if intent_data['action'] == 'edit' else None,
                    user_id=current_user.id,
                    session_id=session_id
                )
            
            return ChatResponse(
                message=response_message,
                session_id=session_id,
                task_id=task_id,
                task_type=intent_data['action'],
                status="processing",
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Regular conversation
        crud.create_chat_message(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            role="assistant",
            message=response_message,
            extra_data={"intent": intent_data}
        )
        
        return ChatResponse(
            message=response_message,
            session_id=session_id,
            status="completed",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get status of a chat task"""
    try:
        # Check in-memory task storage first
        if task_id in chat_tasks_db:
            task_data = chat_tasks_db[task_id]
            return {
                "task_id": task_id,
                "status": task_data.get("status", "unknown"),
                "progress": task_data.get("progress", 0),
                "result_url": task_data.get("result_url"),
                "error": task_data.get("error")
            }
        
        # Fallback to database
        task = crud.get_task_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return {
            "task_id": task_id,
            "status": task.status,
            "progress": 100 if task.status == "completed" else 0,
            "result_url": task.result_url,
            "error": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    try:
        messages = crud.get_chat_history(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            limit=100
        )
        
        return {
            "session_id": session_id,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "message": msg.message,
                    "extra_data": msg.extra_data,
                    "timestamp": msg.timestamp
                }
                for msg in reversed(messages)  # Reverse to show oldest first
            ]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )
