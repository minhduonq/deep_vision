"""
CRUD operations for database
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from backend.database.models import User, ChatMessage, ChatSession, TaskHistory, APIKey


# ==================== USER OPERATIONS ====================

def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    full_name: Optional[str] = None
) -> User:
    """Create new user"""
    user = User(
        username=username,
        email=email,
        full_name=full_name
    )
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Created user: {username}")
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not user.verify_password(password):
        return None
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Update user information"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


# ==================== CHAT OPERATIONS ====================

def create_or_update_chat_session(
    db: Session,
    user_id: int,
    session_id: str,
    title: Optional[str] = None,
    task_type: str = "chat"
) -> ChatSession:
    """Create new chat session or update existing one"""
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == user_id
    ).first()
    
    if session:
        # Update existing session
        if title and not session.title:
            session.title = title
        session.updated_at = datetime.utcnow()
    else:
        # Create new session
        session = ChatSession(
            user_id=user_id,
            session_id=session_id,
            title=title or f"Chat {session_id[:8]}",
            task_type=task_type
        )
        db.add(session)
    
    db.commit()
    db.refresh(session)
    return session


def get_chat_session(db: Session, session_id: str, user_id: int) -> Optional[ChatSession]:
    """Get chat session by ID"""
    return db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == user_id
    ).first()


def get_user_chat_sessions(
    db: Session,
    user_id: int,
    limit: int = 50
) -> List[ChatSession]:
    """Get all chat sessions for a user"""
    return db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).order_by(desc(ChatSession.updated_at)).limit(limit).all()


def create_chat_message(
    db: Session,
    user_id: int,
    session_id: str,
    role: str,
    message: str,
    extra_data: Optional[Dict] = None
) -> ChatMessage:
    """Create new chat message"""
    chat = ChatMessage(
        user_id=user_id,
        session_id=session_id,
        role=role,
        message=message,
        extra_data=extra_data
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_chat_history(
    db: Session,
    user_id: int,
    session_id: Optional[str] = None,
    limit: int = 100
) -> List[ChatMessage]:
    """Get chat history for user"""
    query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    
    if session_id:
        query = query.filter(ChatMessage.session_id == session_id)
    
    return query.order_by(desc(ChatMessage.timestamp)).limit(limit).all()


def get_user_sessions(db: Session, user_id: int) -> List[str]:
    """Get all session IDs for a user"""
    sessions = db.query(ChatMessage.session_id).filter(
        ChatMessage.user_id == user_id
    ).distinct().all()
    
    return [s[0] for s in sessions]


def delete_chat_session(db: Session, user_id: int, session_id: str) -> int:
    """Delete all messages in a session"""
    deleted = db.query(ChatMessage).filter(
        and_(
            ChatMessage.user_id == user_id,
            ChatMessage.session_id == session_id
        )
    ).delete()
    db.commit()
    return deleted


# ==================== TASK OPERATIONS ====================

def create_task(
    db: Session,
    user_id: int,
    task_id: str,
    task_type: str,
    prompt: Optional[str] = None,
    parameters: Optional[Dict] = None
) -> TaskHistory:
    """Create new task"""
    task = TaskHistory(
        user_id=user_id,
        task_id=task_id,
        task_type=task_type,
        prompt=prompt,
        parameters=parameters
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_by_id(db: Session, task_id: str) -> Optional[TaskHistory]:
    """Get task by ID"""
    return db.query(TaskHistory).filter(TaskHistory.task_id == task_id).first()


def update_task(
    db: Session,
    task_id: str,
    **kwargs
) -> Optional[TaskHistory]:
    """Update task"""
    task = get_task_by_id(db, task_id)
    if not task:
        return None
    
    for key, value in kwargs.items():
        if hasattr(task, key):
            setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    return task


def get_user_tasks(
    db: Session,
    user_id: int,
    task_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
) -> List[TaskHistory]:
    """Get user's task history"""
    query = db.query(TaskHistory).filter(TaskHistory.user_id == user_id)
    
    if task_type:
        query = query.filter(TaskHistory.task_type == task_type)
    
    if status:
        query = query.filter(TaskHistory.status == status)
    
    return query.order_by(desc(TaskHistory.created_at)).limit(limit).all()


def get_recent_tasks(db: Session, user_id: int, days: int = 7) -> List[TaskHistory]:
    """Get recent tasks within specified days"""
    since = datetime.utcnow() - timedelta(days=days)
    return db.query(TaskHistory).filter(
        and_(
            TaskHistory.user_id == user_id,
            TaskHistory.created_at >= since
        )
    ).order_by(desc(TaskHistory.created_at)).all()


# ==================== API KEY OPERATIONS ====================

def create_api_key(
    db: Session,
    user_id: int,
    name: Optional[str] = None
) -> APIKey:
    """Create new API key for user"""
    api_key = APIKey(
        user_id=user_id,
        key=APIKey.generate_key(),
        name=name
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    logger.info(f"Created API key for user {user_id}")
    return api_key


def get_user_by_api_key(db: Session, api_key: str) -> Optional[User]:
    """Get user by API key"""
    key_obj = db.query(APIKey).filter(
        and_(
            APIKey.key == api_key,
            APIKey.is_active == True
        )
    ).first()
    
    if not key_obj:
        return None
    
    # Update last used
    key_obj.last_used = datetime.utcnow()
    db.commit()
    
    return key_obj.user


def revoke_api_key(db: Session, key_id: int) -> bool:
    """Revoke API key"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        return False
    
    key.is_active = False
    db.commit()
    return True


# ==================== STATISTICS ====================

def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Get user statistics"""
    total_tasks = db.query(TaskHistory).filter(TaskHistory.user_id == user_id).count()
    completed_tasks = db.query(TaskHistory).filter(
        and_(
            TaskHistory.user_id == user_id,
            TaskHistory.status == "completed"
        )
    ).count()
    total_messages = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).count()
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": total_tasks - completed_tasks,
        "total_messages": total_messages,
        "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }