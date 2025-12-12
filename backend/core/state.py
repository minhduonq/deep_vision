"""
State management for Deep Vision workflow
"""
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    """Types of tasks"""
    DEBLUR = "deblur"
    INPAINT = "inpaint"
    BEAUTY_ENHANCE = "beauty_enhance"
    GENERATE = "generate"
    UNKNOWN = "unknown"


class TaskStatus(str, Enum):
    """Task status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    QUALITY_CHECK = "quality_check"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowState(BaseModel):
    """State for the multi-agent workflow"""
    
    # Task identification
    task_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    # User input
    user_request: str
    image_path: Optional[str] = None
    prompt: Optional[str] = None
    
    # File paths
    input_path: Optional[str] = None  # Input image path
    output_path: Optional[str] = None  # Output image path
    
    # Task analysis
    task_type: TaskType = TaskType.UNKNOWN
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing
    current_agent: str = "coordinator"
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0  # 0 to 100
    
    # Results
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)
    result_path: Optional[str] = None
    
    # Error handling
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    processing_time: Optional[float] = None
    model_used: Optional[str] = None
    quality_score: Optional[float] = None
    
    class Config:
        use_enum_values = True
    
    def update_status(self, status: TaskStatus, progress: Optional[float] = None):
        """Update task status and optionally progress"""
        self.status = status
        if progress is not None:
            self.progress = progress
    
    def add_intermediate_result(self, agent: str, result: Any):
        """Add intermediate result from an agent"""
        self.intermediate_results.append({
            "agent": agent,
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
    
    def increment_retry(self) -> bool:
        """Increment retry counter and return if should retry"""
        self.retry_count += 1
        return self.retry_count < self.max_retries
    
    def set_error(self, error: str):
        """Set error and update status"""
        self.error = error
        self.status = TaskStatus.FAILED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()


class EnhancementRequest(BaseModel):
    """Request model for image enhancement"""
    task_type: Literal["deblur", "inpaint", "beauty_enhance"]
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class GenerationRequest(BaseModel):
    """Request model for image generation"""
    prompt: str
    negative_prompt: Optional[str] = None
    num_images: int = Field(default=1, ge=1, le=4)
    width: int = Field(default=512, ge=256, le=1024)
    height: int = Field(default=512, ge=256, le=1024)
    guidance_scale: float = Field(default=3.5, ge=1.0, le=10.0)  # FLUX uses lower guidance
    num_inference_steps: int = Field(default=8, ge=1, le=16)  # FLUX.1-schnell max is 16
    seed: Optional[int] = None


class TaskResponse(BaseModel):
    """Response model for task creation"""
    task_id: str
    status: str
    message: str
    estimated_time: Optional[int] = None  # seconds


class TaskStatusResponse(BaseModel):
    """Response model for task status check"""
    task_id: str
    status: str
    progress: float
    current_agent: Optional[str] = None
    error: Optional[str] = None
    result_url: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "task_id": "task_abc123",
                "status": "completed",
                "progress": 100.0,
                "result_url": "/static/result.png"
            }
        }


class TaskResultResponse(BaseModel):
    """Response model for task result"""
    task_id: str
    status: str
    result_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time: Optional[float] = None
