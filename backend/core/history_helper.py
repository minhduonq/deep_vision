"""
Task History Integration
Helper functions to save task and chat history automatically
"""
from sqlalchemy.orm import Session
from backend.database import crud
from backend.database.database import get_db
from loguru import logger
from typing import Optional, Dict
import uuid


def generate_session_id() -> str:
    """Generate unique session ID"""
    return f"session_{uuid.uuid4().hex[:12]}"


def save_task_with_chat(
    db: Session,
    user_id: int,
    task_id: str,
    task_type: str,
    prompt: Optional[str] = None,
    parameters: Optional[Dict] = None,
    session_id: Optional[str] = None
) -> str:
    """
    Save task to history and create initial chat message
    Returns session_id
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = generate_session_id()
        
        # Create or update chat session with title from prompt
        title = prompt[:100] if prompt and len(prompt) <= 100 else (prompt[:97] + "..." if prompt else f"{task_type.title()} Task")
        crud.create_or_update_chat_session(
            db=db,
            user_id=user_id,
            session_id=session_id,
            title=title,
            task_type=task_type
        )
        
        # Save task to history
        crud.create_task(
            db=db,
            user_id=user_id,
            task_id=task_id,
            task_type=task_type,
            prompt=prompt,
            parameters=parameters
        )
        
        # Create user message in chat history
        user_message = f"[{task_type.upper()}] {prompt or 'Processing image'}"
        crud.create_chat_message(
            db=db,
            user_id=user_id,
            session_id=session_id,
            role="user",
            message=user_message,
            extra_data={
                "task_id": task_id,
                "task_type": task_type,
                "parameters": parameters
            }
        )
        
        logger.info(f"Saved task {task_id} with chat history for user {user_id}")
        return session_id
        
    except Exception as e:
        logger.error(f"Failed to save task with chat: {e}")
        return session_id or generate_session_id()


def update_task_result(
    db: Session,
    user_id: int,
    task_id: str,
    session_id: str,
    status: str,
    result_path: Optional[str] = None,
    error_message: Optional[str] = None
):
    """
    Update task status and add assistant response to chat
    """
    try:
        # Update task status
        crud.update_task(
            db=db,
            task_id=task_id,
            status=status,
            result_url=result_path,
            error_message=error_message
        )
        
        # Create assistant message
        if status == "completed" and result_path:
            assistant_message = f"✅ Task completed successfully! Your image is ready."
            extra_data = {
                "task_id": task_id,
                "result_path": result_path,
                "status": "success"
            }
        elif status == "failed":
            assistant_message = f"❌ Task failed: {error_message or 'Unknown error'}"
            extra_data = {
                "task_id": task_id,
                "status": "failed",
                "error": error_message
            }
        else:
            # Processing status
            assistant_message = f"🔄 Task is being processed..."
            extra_data = {
                "task_id": task_id,
                "status": status
            }
        
        crud.create_chat_message(
            db=db,
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            message=assistant_message,
            extra_data=extra_data
        )
        
        logger.info(f"Updated task {task_id} result with status: {status}")
        
    except Exception as e:
        logger.error(f"Failed to update task result: {e}")


def get_or_create_session(db: Session, user_id: int, session_id: Optional[str] = None) -> str:
    """
    Get existing session or create new one
    """
    if session_id:
        # Check if session exists
        messages = crud.get_chat_history(db=db, user_id=user_id, session_id=session_id, limit=1)
        if messages:
            return session_id
    
    # Create new session
    return generate_session_id()
