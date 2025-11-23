# 🤖 Multi-Agent System - Quick Start Guide

## Bạn vừa tạo được gì?

### 1. **Hệ thống Multi-Agent hoàn chỉnh** ✅

```
TaskAnalyzer → ImageWorker → QualityControl
     ↓              ↓              ↓
  (phân tích)   (xử lý)      (kiểm tra)
```

### 2. **Các file đã tạo**

#### Core System:
- `backend/agents/base_agent.py` - Base classes cho tất cả agents
- `backend/agents/task_analyzer.py` - Agent phân tích yêu cầu
- `backend/agents/image_worker.py` - Agent xử lý ảnh
- `backend/agents/quality_control.py` - Agent kiểm tra chất lượng
- `backend/agents/orchestrator.py` - Điều phối agents

#### Documentation:
- `AGENT_TUTORIAL.md` - Hướng dẫn chi tiết (đọc đầu tiên!)
- `examples/README.md` - Examples và use cases
- `examples/agent_usage_example.py` - Code mẫu
- `demo_agents.py` - Demo interactive

## 🚀 Cách sử dụng

### Option 1: Simple (No LLM - Tiết kiệm chi phí)

```python
from backend.core.state import WorkflowState, TaskType
from backend.agents.orchestrator import SimpleOrchestrator

# Create state
state = WorkflowState(
    task_id="task_001",
    user_request="Làm rõ ảnh",
    input_path="path/to/image.jpg"
)
state.task_type = TaskType.DEBLUR  # Set manually

# Run without LLM
orchestrator = SimpleOrchestrator(use_llm_analyzer=False)
result = await orchestrator.run(state)

print(f"Output: {result.output_path}")
```

### Option 2: Smart (With LLM - Tự động phân tích)

```python
# Don't set task_type - let LLM decide!
state = WorkflowState(
    task_id="task_002",
    user_request="Xóa người ở phía sau",
    input_path="path/to/image.jpg"
)

# Use LLM analyzer
orchestrator = SimpleOrchestrator(use_llm_analyzer=True)
result = await orchestrator.run(state)

# LLM tự động phát hiện task_type
print(f"Detected: {result.task_type.value}")
print(f"Output: {result.output_path}")
```

### Option 3: Rule-Based (Fastest - Không cần API)

```python
from backend.agents.task_analyzer import SimpleTaskAnalyzer

analyzer = SimpleTaskAnalyzer()
result = await analyzer.analyze("Làm rõ ảnh mờ")

print(f"Task: {result['task_type']}")
print(f"Confidence: {result['confidence']}")
```

## 📊 Agent Flow

```python
# 1. User request comes in
state = WorkflowState(
    user_request="Remove background",
    input_path="photo.jpg"
)

# 2. TaskAnalyzer determines task type
# state.task_type = INPAINT
# state.progress = 20%

# 3. ImageWorker processes image
# → Calls Replicate API
# → Saves output
# state.progress = 70%

# 4. QualityControl validates
# → Checks file exists
# → Validates format
# → Compares with input
# state.progress = 100%
# state.status = COMPLETED
```

## 🎯 3 Cách tích hợp vào FastAPI

### Cách 1: Background Task (Recommended)

```python
from backend.agents.orchestrator import get_orchestrator

@app.post("/api/v1/process")
async def process_image(
    file: UploadFile,
    request: str,
    background_tasks: BackgroundTasks
):
    # Save file
    file_path = await save_file(file)
    task_id = generate_task_id()
    
    # Store initial state
    tasks_db[task_id] = {
        "status": "pending",
        "progress": 0
    }
    
    # Run in background
    background_tasks.add_task(
        run_agent_workflow,
        task_id,
        request,
        file_path
    )
    
    return {"task_id": task_id}

async def run_agent_workflow(task_id: str, request: str, file_path: str):
    # Create state
    state = WorkflowState(
        task_id=task_id,
        user_request=request,
        input_path=file_path
    )
    
    # Run orchestrator
    orchestrator = get_orchestrator(use_llm_analyzer=True)
    result = await orchestrator.run(state)
    
    # Update database
    tasks_db[task_id] = {
        "status": result.status.value,
        "progress": result.progress,
        "output_path": result.output_path,
        "errors": result.intermediate_results.get("errors", [])
    }
```

### Cách 2: Direct Call (For Simple Cases)

```python
@app.post("/api/v1/deblur")
async def deblur_image(file: UploadFile):
    # Save file
    file_path = await save_file(file)
    
    # Create state
    state = WorkflowState(
        task_id=generate_task_id(),
        user_request="deblur",
        input_path=file_path
    )
    state.task_type = TaskType.DEBLUR
    
    # Run (no analyzer needed)
    orchestrator = SimpleOrchestrator(use_llm_analyzer=False)
    result = await orchestrator.run(state)
    
    # Return result directly
    if result.status == TaskStatus.COMPLETED:
        return FileResponse(result.output_path)
    else:
        raise HTTPException(500, detail="Processing failed")
```

### Cách 3: Individual Agents (For Custom Workflows)

```python
from backend.agents import ImageWorkerAgent, QualityControlAgent

@app.post("/api/v1/custom")
async def custom_workflow(file: UploadFile, task_type: str):
    # Create state
    state = WorkflowState(
        task_id=generate_task_id(),
        input_path=await save_file(file)
    )
    state.task_type = TaskType[task_type.upper()]
    
    # Run only worker (skip analyzer)
    worker = ImageWorkerAgent()
    state = await worker.process(state)
    
    # Run QC
    qc = QualityControlAgent()
    state = await qc.process(state)
    
    return {
        "output": state.output_path,
        "status": state.status.value
    }
```

## 🔧 Advanced: Custom Agent

```python
from backend.agents.base_agent import BaseAgent
from backend.core.state import WorkflowState, TaskStatus

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("My Custom Agent")
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        # Your custom logic
        state.status = TaskStatus.PROCESSING
        
        # Do something with state.input_path
        # ...
        
        state.output_path = "custom_output.jpg"
        state.status = TaskStatus.COMPLETED
        
        return state

# Use it in orchestrator
orchestrator = SimpleOrchestrator(use_llm_analyzer=False)
orchestrator.agents.append(MyCustomAgent())
```

## 📚 Đọc gì tiếp theo?

1. **AGENT_TUTORIAL.md** - Giải thích chi tiết từng concept
2. **examples/README.md** - Nhiều use cases khác nhau
3. **examples/agent_usage_example.py** - Code examples

## 🧪 Test ngay

```bash
# Demo interactive
python demo_agents.py

# Run examples
python examples/agent_usage_example.py
```

## 💡 Tips

### Development:
- Dùng `SimpleTaskAnalyzer` để tiết kiệm OpenAI credits
- Set `task_type` manually trong development
- Log mọi thứ để debug

### Production:
- Dùng `TaskAnalyzerAgent` với LLM cho accuracy cao
- Enable QualityControl để validate outputs
- Monitor `state.intermediate_results` for insights

### Testing:
```python
# Test individual agent
analyzer = TaskAnalyzerAgent()
state = await analyzer.process(test_state)
assert state.task_type == TaskType.INPAINT

# Test full workflow
orchestrator = SimpleOrchestrator()
result = await orchestrator.run(test_state)
assert result.status == TaskStatus.COMPLETED
```

## ❓ Troubleshooting

**Q: LLM analyzer fails?**
```python
# Use simple analyzer instead
orchestrator = SimpleOrchestrator(use_llm_analyzer=False)
```

**Q: Want to skip QC?**
```python
# Remove QC agent
orchestrator.agents = [
    TaskAnalyzerAgent(),
    ImageWorkerAgent()
]
```

**Q: Need retry logic?**
```python
# Use ConditionalOrchestrator
from backend.agents.orchestrator import ConditionalOrchestrator
orchestrator = ConditionalOrchestrator()
```

## 🎓 Key Concepts

1. **State** - Shared data structure, passed through agents
2. **Agents** - Independent workers, single responsibility
3. **Orchestrator** - Coordinates agent execution
4. **Base Classes** - Provide common functionality (logging, error handling)

## Next Steps

✅ Bạn đã có hệ thống multi-agent hoàn chỉnh!

Giờ bạn có thể:
1. Tích hợp vào FastAPI backend hiện tại
2. Thêm custom agents cho use cases riêng
3. Scale với Celery hoặc Ray cho distributed processing
4. Add streaming để user thấy real-time progress

**Happy coding!** 🚀
