"""
History API Routes
Get user's chat history and task history
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from loguru import logger

from backend.database.database import get_db
from backend.database import crud
from backend.auth.jwt import decode_token

router = APIRouter(prefix="/api/v1/history", tags=["history"])
security = HTTPBearer()


# ==================== SCHEMAS ====================

class TaskHistoryItem(BaseModel):
    """Schema for task history item"""
    id: int
    task_id: str
    task_type: str
    prompt: Optional[str] = None
    status: str
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_task(cls, task):
        """Convert TaskHistory model to schema"""
        return cls(
            id=task.id,
            task_id=task.task_id,
            task_type=task.task_type,
            prompt=task.prompt,
            status=task.status,
            result_url=task.output_path,  # Map output_path to result_url
            error_message=task.error_message,
            created_at=task.created_at,
            completed_at=task.completed_at
        )


class ChatSessionItem(BaseModel):
    """Schema for chat session"""
    session_id: str
    title: str
    task_type: str
    message_count: int
    last_message: str
    last_timestamp: datetime
    created_at: datetime


class HistoryResponse(BaseModel):
    """Combined history response"""
    tasks: List[TaskHistoryItem]
    sessions: List[ChatSessionItem]
    total_tasks: int
    total_sessions: int


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


# ==================== ENDPOINTS ====================

@router.get("/tasks", response_model=List[TaskHistoryItem])
async def get_task_history(
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get task history for current user
    
    - **task_type**: Filter by type (generate, enhance, edit, etc.)
    - **status**: Filter by status (completed, failed, processing)
    - **limit**: Maximum number of results (1-100)
    """
    try:
        tasks = crud.get_user_tasks(
            db=db,
            user_id=current_user.id,
            task_type=task_type,
            status=status,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(tasks)} tasks for user {current_user.username}")
        
        return [TaskHistoryItem.from_task(task) for task in tasks]
        
    except Exception as e:
        logger.error(f"Error retrieving task history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task history: {str(e)}"
        )


@router.get("/sessions", response_model=List[ChatSessionItem])
async def get_chat_sessions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all chat sessions for current user with titles
    """
    try:
        # Get sessions from ChatSession table
        db_sessions = crud.get_user_chat_sessions(db=db, user_id=current_user.id, limit=100)
        
        sessions = []
        for session in db_sessions:
            # Get last message
            messages = crud.get_chat_history(
                db=db,
                user_id=current_user.id,
                session_id=session.session_id,
                limit=1
            )
            
            last_message = ""
            last_timestamp = session.updated_at
            
            if messages:
                last_msg = messages[0]
                last_message = last_msg.message[:100] + "..." if len(last_msg.message) > 100 else last_msg.message
                last_timestamp = last_msg.timestamp
            
            # Get message count
            all_messages = crud.get_chat_history(
                db=db,
                user_id=current_user.id,
                session_id=session.session_id,
                limit=10000
            )
            
            sessions.append(ChatSessionItem(
                session_id=session.session_id,
                title=session.title,
                task_type=session.task_type,
                message_count=len(all_messages),
                last_message=last_message or "No messages yet",
                last_timestamp=last_timestamp,
                created_at=session.created_at
            ))
        
        logger.info(f"Retrieved {len(sessions)} sessions for user {current_user.username}")
        
        return sessions
        
    except Exception as e:
        logger.error(f"Error retrieving chat sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat sessions: {str(e)}"
        )


@router.get("/", response_model=HistoryResponse)
async def get_full_history(
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get combined history (tasks + chat sessions) for current user
    """
    try:
        # Get tasks
        db_tasks = crud.get_user_tasks(
            db=db,
            user_id=current_user.id,
            limit=50
        )
        tasks = [TaskHistoryItem.from_task(task) for task in db_tasks]
        
        # Get sessions from ChatSession table
        db_sessions = crud.get_user_chat_sessions(db=db, user_id=current_user.id, limit=limit)
        sessions = []
        
        for session in db_sessions:
            messages = crud.get_chat_history(
                db=db,
                user_id=current_user.id,
                session_id=session.session_id,
                limit=1
            )
            
            last_message = ""
            last_timestamp = session.updated_at
            
            if messages:
                last_msg = messages[0]
                last_message = last_msg.message[:100] + "..." if len(last_msg.message) > 100 else last_msg.message
                last_timestamp = last_msg.timestamp
            
            all_messages = crud.get_chat_history(
                db=db,
                user_id=current_user.id,
                session_id=session.session_id,
                limit=10000
            )
            
            sessions.append(ChatSessionItem(
                session_id=session.session_id,
                title=session.title,
                task_type=session.task_type,
                message_count=len(all_messages),
                last_message=last_message or "No messages yet",
                last_timestamp=last_timestamp,
                created_at=session.created_at
            ))
        
        return HistoryResponse(
            tasks=tasks,
            sessions=sessions,
            total_tasks=len(tasks),
            total_sessions=len(sessions)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving full history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )


@router.get("/recent", response_model=List[TaskHistoryItem])
async def get_recent_tasks(
    days: int = Query(7, ge=1, le=30, description="Number of days"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent tasks within specified days
    """
    try:
        tasks = crud.get_recent_tasks(
            db=db,
            user_id=current_user.id,
            days=days
        )
        
        logger.info(f"Retrieved {len(tasks)} recent tasks for user {current_user.username}")
        
        return [TaskHistoryItem.from_task(task) for task in tasks]
        
    except Exception as e:
        logger.error(f"Error retrieving recent tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent tasks: {str(e)}"
        )
