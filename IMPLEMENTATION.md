# Implementation Guide - Multi-Agent System

## 📋 Hướng dẫn triển khai từng bước

Guide này sẽ hướng dẫn bạn implement từng agent một cách chi tiết.

## Phase 1: Setup cơ bản (Đã hoàn thành ✅)

- [x] Cấu trúc project
- [x] FastAPI backend skeleton
- [x] Streamlit frontend
- [x] Configuration và utilities

## Phase 2: Implement Task Analyzer Agent (Ưu tiên cao)

### Mục đích
Task Analyzer là agent đầu tiên nhận request và quyết định workflow.

### File: `backend/agents/task_analyzer.py`

```python
"""
Task Analyzer Agent
Phân tích user request và xác định task type, parameters
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from backend.core.state import WorkflowState, TaskType
from backend.core.config import settings
from loguru import logger


class TaskAnalyzerAgent:
    """Analyze user requests and determine task parameters"""
    
    def __init__(self):
        # Initialize LLM (OpenAI hoặc Anthropic)
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # Hoặc "gpt-4" cho kết quả tốt hơn
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a task analyzer for an image processing system.
            
Your job is to analyze user requests and extract:
1. Task type (deblur, inpaint, beauty_enhance, or generate)
2. Specific parameters needed for the task
3. Target objects (for inpainting)
4. Enhancement preferences (for beauty enhancement)

Return your analysis in JSON format with these keys:
- task_type: one of [deblur, inpaint, beauty_enhance, generate]
- parameters: dict with relevant parameters
- confidence: float 0-1 indicating your confidence
- reasoning: brief explanation of your analysis

Examples:

User: "Remove the person in the background"
Response: {
    "task_type": "inpaint",
    "parameters": {"target": "person in background", "preserve_foreground": true},
    "confidence": 0.95,
    "reasoning": "User explicitly wants to remove an object"
}

User: "Make this photo clearer and sharper"
Response: {
    "task_type": "deblur", 
    "parameters": {"strength": "medium"},
    "confidence": 0.9,
    "reasoning": "User wants to improve image sharpness"
}

User: "Smooth skin and brighten the face"
Response: {
    "task_type": "beauty_enhance",
    "parameters": {"skin_smoothing": true, "brightening": true},
    "confidence": 0.95,
    "reasoning": "User wants facial beauty enhancements"
}
"""),
            ("human", "User request: {request}\nTask type hint: {task_type_hint}\n\nAnalyze this request:")
        ])
    
    async def analyze(self, state: WorkflowState) -> WorkflowState:
        """Analyze user request and update state"""
        try:
            logger.info(f"Analyzing task: {state.user_request}")
            
            # Create chain
            chain = self.prompt | self.llm
            
            # Get analysis
            response = await chain.ainvoke({
                "request": state.user_request,
                "task_type_hint": state.task_type if state.task_type != TaskType.UNKNOWN else "unknown"
            })
            
            # Parse response (assuming JSON output)
            import json
            analysis = json.loads(response.content)
            
            # Update state
            state.task_type = TaskType(analysis["task_type"])
            state.parameters = analysis.get("parameters", {})
            state.add_intermediate_result("task_analyzer", {
                "analysis": analysis,
                "confidence": analysis.get("confidence", 0.0)
            })
            
            logger.info(f"Analysis complete: {state.task_type}")
            
        except Exception as e:
            logger.error(f"Task analysis failed: {e}")
            state.set_error(f"Task analysis failed: {str(e)}")
        
        return state


# Singleton instance
task_analyzer = TaskAnalyzerAgent()
```

### Testing Task Analyzer

```python
# File: backend/agents/test_analyzer.py
import asyncio
from backend.agents.task_analyzer import task_analyzer
from backend.core.state import WorkflowState, TaskType

async def test_analyzer():
    # Test case 1: Deblur
    state1 = WorkflowState(
        task_id="test_1",
        user_request="Make this blurry photo sharper",
        task_type=TaskType.DEBLUR
    )
    result1 = await task_analyzer.analyze(state1)
    print(f"Test 1: {result1.task_type} - {result1.parameters}")
    
    # Test case 2: Inpaint
    state2 = WorkflowState(
        task_id="test_2",
        user_request="Remove the car from the image",
        task_type=TaskType.INPAINT
    )
    result2 = await task_analyzer.analyze(state2)
    print(f"Test 2: {result2.task_type} - {result2.parameters}")

if __name__ == "__main__":
    asyncio.run(test_analyzer())
```

## Phase 3: Implement Model Wrappers (API-First)

### 3.1 Replicate API Wrapper

File: `backend/models/replicate_wrapper.py`

```python
"""
Replicate API Wrapper
Sử dụng Replicate API cho các CV models
"""
import replicate
from typing import Optional, Dict, Any
from pathlib import Path
from backend.core.config import settings
from loguru import logger
import httpx


class ReplicateWrapper:
    """Wrapper for Replicate API"""
    
    def __init__(self):
        if not settings.REPLICATE_API_TOKEN:
            raise ValueError("REPLICATE_API_TOKEN is required")
        
        self.client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)
    
    async def deblur_image(self, image_path: str) -> Optional[str]:
        """
        Deblur image using SwinIR or similar
        Returns URL of processed image
        """
        try:
            logger.info(f"Deblurring image: {image_path}")
            
            # Upload image and get URL
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Use SwinIR for deblurring
            output = await self.client.run(
                "jingyunliang/swinir:660d922d33153019e8c594a6ea8e9f8c7d8e9c9e",
                input={
                    "image": image_data,
                    "task_type": "real_sr",  # Real-world super-resolution
                    "scale": 2
                }
            )
            
            logger.info(f"Deblur complete: {output}")
            return output
            
        except Exception as e:
            logger.error(f"Deblur failed: {e}")
            return None
    
    async def inpaint_image(
        self, 
        image_path: str, 
        mask_path: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Remove objects from image using inpainting
        """
        try:
            logger.info(f"Inpainting image: {image_path}")
            
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # LaMa for inpainting
            if mask_path:
                with open(mask_path, "rb") as f:
                    mask_data = f.read()
            else:
                # TODO: Auto-generate mask using SAM or similar
                mask_data = None
            
            # Use Stable Diffusion Inpainting
            output = await self.client.run(
                "stability-ai/stable-diffusion-inpainting:...",
                input={
                    "image": image_data,
                    "mask": mask_data,
                    "prompt": prompt or "remove the object"
                }
            )
            
            return output
            
        except Exception as e:
            logger.error(f"Inpainting failed: {e}")
            return None
    
    async def enhance_face(self, image_path: str) -> Optional[str]:
        """
        Enhance facial features using GFPGAN or CodeFormer
        """
        try:
            logger.info(f"Enhancing face: {image_path}")
            
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Use GFPGAN
            output = await self.client.run(
                "tencentarc/gfpgan:...",
                input={
                    "image": image_data,
                    "version": "v1.4",
                    "scale": 2
                }
            )
            
            return output
            
        except Exception as e:
            logger.error(f"Face enhancement failed: {e}")
            return None
    
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Optional[str]:
        """
        Generate image from text prompt
        """
        try:
            logger.info(f"Generating image: {prompt[:50]}...")
            
            output = await self.client.run(
                "stability-ai/sdxl:...",
                input={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "seed": seed
                }
            )
            
            return output
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None


# Singleton
replicate_wrapper = ReplicateWrapper()
```

## Phase 4: Implement Enhancement Agent

File: `backend/agents/enhancement_agent.py`

```python
"""
Enhancement Agent
Orchestrates image enhancement tasks
"""
from backend.core.state import WorkflowState, TaskType, TaskStatus
from backend.models.replicate_wrapper import replicate_wrapper
from backend.core.config import settings
from loguru import logger
from pathlib import Path
import httpx


class EnhancementAgent:
    """Agent for image enhancement tasks"""
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """Process enhancement request"""
        try:
            state.update_status(TaskStatus.PROCESSING, 10)
            
            # Route to appropriate specialist
            if state.task_type == TaskType.DEBLUR:
                result = await self._deblur(state)
            elif state.task_type == TaskType.INPAINT:
                result = await self._inpaint(state)
            elif state.task_type == TaskType.BEAUTY_ENHANCE:
                result = await self._beauty_enhance(state)
            else:
                raise ValueError(f"Unsupported task type: {state.task_type}")
            
            if result:
                state.update_status(TaskStatus.QUALITY_CHECK, 90)
                state.result_path = result
            else:
                raise Exception("Processing failed")
                
        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            state.set_error(str(e))
        
        return state
    
    async def _deblur(self, state: WorkflowState) -> Optional[str]:
        """Deblur image"""
        logger.info("Processing deblur task")
        state.update_status(TaskStatus.PROCESSING, 30)
        
        # Call model
        result_url = await replicate_wrapper.deblur_image(state.image_path)
        
        if result_url:
            # Download result
            result_path = await self._download_result(result_url, state.task_id)
            state.update_status(TaskStatus.PROCESSING, 80)
            return result_path
        
        return None
    
    async def _inpaint(self, state: WorkflowState) -> Optional[str]:
        """Remove objects from image"""
        logger.info("Processing inpaint task")
        # Similar to deblur
        pass
    
    async def _beauty_enhance(self, state: WorkflowState) -> Optional[str]:
        """Enhance facial features"""
        logger.info("Processing beauty enhancement")
        # Similar to deblur
        pass
    
    async def _download_result(self, url: str, task_id: str) -> str:
        """Download result from URL"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            result_path = settings.OUTPUT_DIR / f"{task_id}_result.png"
            with open(result_path, "wb") as f:
                f.write(response.content)
            
            return str(result_path)


# Singleton
enhancement_agent = EnhancementAgent()
```

## Phase 5: Integrate với FastAPI

Update `backend/api/main.py` để sử dụng agents:

```python
# Thêm vào đầu file
from backend.agents.task_analyzer import task_analyzer
from backend.agents.enhancement_agent import enhancement_agent

# Background task processor
async def process_enhancement_task(task_id: str):
    """Background task to process enhancement"""
    try:
        task = tasks_db[task_id]
        
        # Create workflow state
        state = WorkflowState(
            task_id=task_id,
            user_request=task.get("description", ""),
            image_path=task["file_path"],
            task_type=TaskType(task["task_type"])
        )
        
        # Analyze task (if description provided)
        if state.user_request:
            state = await task_analyzer.analyze(state)
        
        # Process enhancement
        state = await enhancement_agent.process(state)
        
        # Update task in database
        if state.status == TaskStatus.COMPLETED:
            tasks_db[task_id]["status"] = "completed"
            tasks_db[task_id]["result_path"] = state.result_path
            tasks_db[task_id]["progress"] = 100
        else:
            tasks_db[task_id]["status"] = "failed"
            tasks_db[task_id]["error"] = state.error
            
    except Exception as e:
        logger.error(f"Task processing failed: {e}")
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)

# Uncomment dòng này trong endpoint /api/v1/enhance
# background_tasks.add_task(process_enhancement_task, task_id)
```

## Testing End-to-End

```powershell
# Terminal 1: Start backend
python backend/api/main.py

# Terminal 2: Start frontend
streamlit run frontend/streamlit_app.py

# Terminal 3: Test API
curl -X POST http://localhost:8000/api/v1/enhance `
  -F "file=@test_image.jpg" `
  -F "task_type=deblur" `
  -F "description=Make this image sharper"
```

## Next Implementation Steps

1. ✅ Implement Task Analyzer Agent
2. ✅ Implement Replicate API Wrapper  
3. ✅ Implement Enhancement Agent
4. ⬜ Implement Generation Agent
5. ⬜ Implement Quality Control Agent
6. ⬜ Add LangGraph orchestration
7. ⬜ Add proper error handling
8. ⬜ Add caching
9. ⬜ Add monitoring
10. ⬜ Deploy

## Deployment Checklist

- [ ] Setup environment variables
- [ ] Configure API keys
- [ ] Test all endpoints
- [ ] Add rate limiting
- [ ] Add authentication
- [ ] Setup logging
- [ ] Setup monitoring
- [ ] Docker containerization
- [ ] Deploy to cloud (Railway, Render, AWS, etc.)

## Resources

- Replicate Models: https://replicate.com/explore
- LangChain Docs: https://python.langchain.com/
- FastAPI Docs: https://fastapi.tiangolo.com/

Good luck! 🚀
