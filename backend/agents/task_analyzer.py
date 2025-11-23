"""
Task Analyzer Agent - Analyzes user requests to determine task type and parameters
"""
import json
from typing import Dict, Any
from loguru import logger
from openai import AsyncOpenAI

from backend.core.state import WorkflowState, TaskType, TaskStatus
from backend.core.config import settings
from backend.agents.base_agent import LLMAgent


class TaskAnalyzerAgent(LLMAgent):
    """
    Analyzes user requests using LLM to determine:
    - Task type (deblur, inpaint, beauty_enhance, generate)
    - Confidence level
    - Additional parameters needed
    """
    
    def __init__(self):
        super().__init__(
            name="Task Analyzer",
            model="gpt-4",
            temperature=0.3  # Low temperature for consistent analysis
        )
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("Task Analyzer Agent initialized with OpenAI")
    
    def create_prompt(self, state: WorkflowState) -> str:
        """Create prompt for task analysis"""
        return f"""Bạn là một AI expert phân tích yêu cầu xử lý ảnh.

Yêu cầu của user: "{state.user_request}"

Phân tích yêu cầu và xác định task_type phù hợp nhất:

**Task Types:**
1. **deblur**: Làm sắc nét ảnh mờ, khử mờ
   - Ví dụ: "làm rõ ảnh", "xóa blur", "ảnh bị mờ"

2. **inpaint**: Xóa object, sửa đổi vùng trong ảnh
   - Ví dụ: "xóa object", "xóa người", "remove background", "bỏ chữ"

3. **beauty_enhance**: Làm đẹp khuôn mặt, chỉnh sửa portrait
   - Ví dụ: "làm đẹp", "beautify", "chỉnh sửa da", "làm đẹp khuôn mặt"

4. **generate**: Tạo ảnh mới từ text prompt
   - Ví dụ: "tạo ảnh", "generate image", "vẽ cho tôi"

Trả về JSON với format chính xác:
{{
    "task_type": "deblur" | "inpaint" | "beauty_enhance" | "generate",
    "confidence": 0.0-1.0,
    "reasoning": "Giải thích tại sao chọn task này",
    "suggested_params": {{
        "key": "value"
    }}
}}

Chỉ trả về JSON, không thêm text khác."""

    async def process(self, state: WorkflowState) -> WorkflowState:
        """
        Analyze user request and update state
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with task_type determined
        """
        try:
            # Update status
            state.status = TaskStatus.ANALYZING
            state.progress = 10
            
            # Create prompt
            prompt = self.create_prompt(state)
            
            # Call OpenAI
            logger.info(f"Analyzing request: {state.user_request[:50]}...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing image processing requests. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            analysis = json.loads(response.choices[0].message.content)
            
            # Update state
            task_type_str = analysis.get("task_type", "deblur")
            
            # Map string to TaskType enum
            task_type_mapping = {
                "deblur": TaskType.DEBLUR,
                "inpaint": TaskType.INPAINT,
                "beauty_enhance": TaskType.BEAUTY_ENHANCE,
                "generate": TaskType.GENERATE
            }
            
            state.task_type = task_type_mapping.get(task_type_str, TaskType.DEBLUR)
            state.progress = 20
            
            # Store analysis results
            state.intermediate_results["analysis"] = {
                "confidence": analysis.get("confidence", 0.8),
                "reasoning": analysis.get("reasoning", ""),
                "suggested_params": analysis.get("suggested_params", {})
            }
            
            logger.info(
                f"Analysis complete - Task: {state.task_type.value}, "
                f"Confidence: {analysis.get('confidence', 0):.2f}"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Task analysis failed: {e}")
            # Default to DEBLUR if analysis fails
            state.task_type = TaskType.DEBLUR
            state.intermediate_results["analysis"] = {
                "confidence": 0.5,
                "reasoning": f"Analysis failed, using default: {str(e)}",
                "error": str(e)
            }
            state.progress = 20
            return state


class SimpleTaskAnalyzer:
    """
    Simple rule-based task analyzer (no LLM needed)
    Use this if you want to save API costs or don't have OpenAI key
    """
    
    def __init__(self):
        self.name = "Simple Task Analyzer"
        
        # Keywords for each task type
        self.keywords = {
            TaskType.DEBLUR: [
                "mờ", "blur", "sắc nét", "sharp", "rõ", "clear", "khử mờ"
            ],
            TaskType.INPAINT: [
                "xóa", "remove", "delete", "bỏ", "object", "người", "background",
                "nền", "chữ", "text", "watermark"
            ],
            TaskType.BEAUTY_ENHANCE: [
                "đẹp", "beauty", "beautify", "da", "skin", "khuôn mặt", "face",
                "portrait", "chỉnh sửa"
            ],
            TaskType.GENERATE: [
                "tạo", "generate", "vẽ", "draw", "create", "sinh"
            ]
        }
    
    async def analyze(self, user_request: str) -> Dict[str, Any]:
        """
        Simple keyword-based analysis
        
        Args:
            user_request: User's request string
            
        Returns:
            Analysis results
        """
        user_request_lower = user_request.lower()
        scores = {}
        
        # Calculate score for each task type
        for task_type, keywords in self.keywords.items():
            score = sum(1 for kw in keywords if kw in user_request_lower)
            scores[task_type] = score
        
        # Get task with highest score
        best_task = max(scores, key=scores.get)
        max_score = scores[best_task]
        
        # If no keywords matched, default to DEBLUR
        if max_score == 0:
            best_task = TaskType.DEBLUR
            confidence = 0.5
        else:
            # Confidence based on score
            confidence = min(0.6 + (max_score * 0.1), 0.95)
        
        return {
            "task_type": best_task.value,
            "confidence": confidence,
            "reasoning": f"Matched {max_score} keywords for {best_task.value}",
            "scores": {t.value: s for t, s in scores.items()}
        }
