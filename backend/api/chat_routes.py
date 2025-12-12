"""
Chat History API Routes
Handles conversation history between users and AI agents
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from loguru import logger

from backend.database.database import get_db
from backend.database import crud
from backend.auth.jwt import decode_token

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
security = HTTPBearer()


# ==================== SCHEMAS ====================

class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    session_id: str = Field(..., description="Session ID to group related messages")
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    message: str = Field(..., description="Message content")
    extra_data: Optional[dict] = Field(None, description="Additional data (images, metadata)")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123abc",
                "role": "user",
                "message": "Generate a beautiful landscape image",
                "extra_data": {
                    "task_id": "task_xyz",
                    "task_type": "generation"
                }
            }
        }


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: int
    user_id: int
    session_id: str
    role: str
    message: str
    extra_data: Optional[dict]
    timestamp: datetime

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """Schema for session information"""
    session_id: str
    message_count: int
    last_message: str
    last_timestamp: datetime


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
    
    user_id = payload.get("user_id")
    user = crud.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


# ==================== ENDPOINTS ====================

@router.post("/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_data: ChatMessageCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new chat message
    
    - **session_id**: Session identifier to group related messages
    - **role**: Either 'user' or 'assistant'
    - **message**: The actual message content
    - **extra_data**: Optional metadata (task_id, images, etc.)
    """
    try:
        # Validate role
        if message_data.role not in ["user", "assistant"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be 'user' or 'assistant'"
            )
        
        # Create message
        chat_message = crud.create_chat_message(
            db=db,
            user_id=current_user.id,
            session_id=message_data.session_id,
            role=message_data.role,
            message=message_data.message,
            extra_data=message_data.extra_data
        )
        
        logger.info(f"Created chat message for user {current_user.username}, session {message_data.session_id}")
        
        return chat_message
        
    except Exception as e:
        logger.error(f"Error creating chat message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create message: {str(e)}"
        )


@router.get("/messages", response_model=List[ChatMessageResponse])
async def get_messages(
    session_id: Optional[str] = None,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history for current user
    
    - **session_id**: Optional - filter by specific session
    - **limit**: Maximum number of messages to return (default 100)
    """
    try:
        messages = crud.get_chat_history(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(messages)} messages for user {current_user.username}")
        
        return messages
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve messages: {str(e)}"
        )


@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all chat sessions for current user
    
    Returns a list of sessions with metadata (message count, last message, etc.)
    """
    try:
        session_ids = crud.get_user_sessions(db=db, user_id=current_user.id)
        
        sessions = []
        for session_id in session_ids:
            messages = crud.get_chat_history(
                db=db,
                user_id=current_user.id,
                session_id=session_id,
                limit=1
            )
            
            if messages:
                last_msg = messages[0]
                # Get total count for session
                all_messages = crud.get_chat_history(
                    db=db,
                    user_id=current_user.id,
                    session_id=session_id,
                    limit=10000
                )
                
                sessions.append(SessionResponse(
                    session_id=session_id,
                    message_count=len(all_messages),
                    last_message=last_msg.message[:100] + "..." if len(last_msg.message) > 100 else last_msg.message,
                    last_timestamp=last_msg.timestamp
                ))
        
        logger.info(f"Retrieved {len(sessions)} sessions for user {current_user.username}")
        
        return sessions
        
    except Exception as e:
        logger.error(f"Error retrieving sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sessions: {str(e)}"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a chat session and all its messages
    
    - **session_id**: The session to delete
    """
    try:
        deleted_count = crud.delete_chat_session(
            db=db,
            user_id=current_user.id,
            session_id=session_id
        )
        
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found"
            )
        
        logger.info(f"Deleted session {session_id} ({deleted_count} messages) for user {current_user.username}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: str,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages from a specific session
    
    - **session_id**: The session to retrieve messages from
    - **limit**: Maximum number of messages to return (default 100)
    """
    try:
        messages = crud.get_chat_history(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            limit=limit
        )
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found or empty"
            )
        
        logger.info(f"Retrieved {len(messages)} messages from session {session_id} for user {current_user.username}")
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session messages: {str(e)}"
        )
