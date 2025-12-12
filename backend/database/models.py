from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from passlib.context import CryptContext
import secrets

Base = declarative_base()

# Configure bcrypt with proper settings for newer versions
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)


class User(Base):
    """User model for authentication"""
    __tablename__ ='users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    chat_history = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    task_history = relationship("TaskHistory", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """Hash and set password"""
        # Truncate password to 72 bytes for bcrypt
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')[:72]
            password = password_bytes.decode('utf-8')
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        # Truncate password to 72 bytes for bcrypt
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')[:72]
            password = password_bytes.decode('utf-8')
        return pwd_context.verify(password, self.password_hash)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
class ChatSession(Base):
    """Chat sessions with titles"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255))  # Session title (first user prompt)
    task_type = Column(String(50))  # 'chat', 'generate', 'enhance', 'edit', etc.
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")


class ChatMessage(Base):
    """Chat history between user and AI"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(50), index=True)  # Group messages by session
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    extra_data = Column(JSON)  # Store additional data (images, attachments, etc.)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_history")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "role": self.role,
            "message": self.message,
            "extra_data": self.extra_data,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class TaskHistory(Base):
    """History of image processing tasks"""
    __tablename__ = "task_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(String(50), unique=True, index=True, nullable=False)
    task_type = Column(String(50), nullable=False)  # 'deblur', 'generation', etc.
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    
    # Paths
    input_path = Column(String(255))
    output_path = Column(String(255))
    
    # Parameters
    prompt = Column(Text)
    parameters = Column(JSON)  # Store all task parameters
    
    # Result data
    result_data = Column(JSON)  # Store results, model info, etc.
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="task_history")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "prompt": self.prompt,
            "parameters": self.parameters,
            "result_data": self.result_data,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class APIKey(Base):
    """API keys for user authentication"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(100))  # Friendly name for the key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    @staticmethod
    def generate_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(48)
    
    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None
        }
