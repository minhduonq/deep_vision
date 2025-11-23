# Hướng dẫn xây dựng hệ thống Multi-Agent đơn giản

## 1. Khái niệm cơ bản

### Agent là gì?
- Agent là một "đơn vị thông minh" có khả năng:
  - Nhận input (đầu vào)
  - Xử lý logic (suy nghĩ, quyết định)
  - Tạo output (kết quả)
  - Gọi tools/APIs nếu cần

### Multi-Agent System
- Nhiều agents làm việc cùng nhau
- Mỗi agent có vai trò riêng
- Agents trao đổi thông tin qua **State** (trạng thái chung)

## 2. Architecture đơn giản

```
User Request
    ↓
┌─────────────────────┐
│  Task Analyzer      │ ← Phân tích yêu cầu
│  (LLM + Prompt)     │
└─────────────────────┘
    ↓ (State)
┌─────────────────────┐
│  Worker Agent       │ ← Xử lý thực tế
│  (Call API/Model)   │
└─────────────────────┘
    ↓ (State)
┌─────────────────────┐
│  Quality Control    │ ← Kiểm tra kết quả
│  (Validation)       │
└─────────────────────┘
    ↓
Result to User
```

## 3. Core Components

### a) State (Trạng thái chung)
```python
class WorkflowState:
    task_id: str
    user_request: str      # Yêu cầu gốc
    task_type: str         # deblur, inpaint, beauty
    status: str            # pending, processing, completed
    progress: int          # 0-100
    input_path: str        # Đường dẫn ảnh đầu vào
    output_path: str       # Đường dẫn ảnh kết quả
    metadata: dict         # Thông tin thêm
    errors: list           # Lỗi nếu có
```

### b) Base Agent Class
```python
class BaseAgent:
    def __init__(self, name: str):
        self.name = name
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        # Mỗi agent implement method này
        raise NotImplementedError
```

### c) Orchestrator (Điều phối)
```python
class Orchestrator:
    def __init__(self):
        self.agents = []
    
    async def run(self, initial_state: WorkflowState):
        state = initial_state
        for agent in self.agents:
            state = await agent.process(state)
            if state.status == "failed":
                break
        return state
```

## 4. Implementation Example

### Step 1: Task Analyzer Agent
```python
class TaskAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Task Analyzer")
        self.llm = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        # Dùng LLM để phân tích yêu cầu
        prompt = f'''
        Phân tích yêu cầu của user và xác định task_type:
        
        User request: {state.user_request}
        
        Trả về JSON:
        {{
            "task_type": "deblur" | "inpaint" | "beauty_enhance",
            "confidence": 0.0-1.0,
            "reasoning": "explanation"
        }}
        '''
        
        response = await self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        state.task_type = result["task_type"]
        state.metadata["confidence"] = result["confidence"]
        state.metadata["reasoning"] = result["reasoning"]
        state.progress = 20
        
        return state
```

### Step 2: Worker Agent
```python
class ImageWorkerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Image Worker")
        self.replicate = replicate_client
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        try:
            state.status = "processing"
            state.progress = 40
            
            # Gọi model tương ứng
            if state.task_type == "deblur":
                output = await self.replicate.deblur_image(state.input_path)
            elif state.task_type == "inpaint":
                output = await self.replicate.inpaint_image(state.input_path)
            elif state.task_type == "beauty_enhance":
                output = await self.replicate.enhance_beauty(state.input_path)
            
            state.output_path = str(output)
            state.progress = 70
            
        except Exception as e:
            state.status = "failed"
            state.errors.append(str(e))
        
        return state
```

### Step 3: Quality Control Agent
```python
class QualityControlAgent(BaseAgent):
    def __init__(self):
        super().__init__("Quality Control")
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        # Kiểm tra kết quả
        if not state.output_path or not Path(state.output_path).exists():
            state.status = "failed"
            state.errors.append("Output file not found")
            return state
        
        # Kiểm tra kích thước file
        file_size = Path(state.output_path).stat().st_size
        if file_size < 1000:  # < 1KB = có vấn đề
            state.status = "failed"
            state.errors.append("Output file too small")
            return state
        
        # Kiểm tra format ảnh
        try:
            from PIL import Image
            img = Image.open(state.output_path)
            state.metadata["output_size"] = img.size
            state.metadata["output_format"] = img.format
        except Exception as e:
            state.status = "failed"
            state.errors.append(f"Invalid image: {e}")
            return state
        
        # Passed all checks
        state.status = "completed"
        state.progress = 100
        
        return state
```

### Step 4: Orchestrator
```python
class ImageProcessingOrchestrator:
    def __init__(self):
        self.agents = [
            TaskAnalyzerAgent(),
            ImageWorkerAgent(),
            QualityControlAgent()
        ]
    
    async def run(self, user_request: str, image_path: str) -> WorkflowState:
        # Khởi tạo state
        state = WorkflowState(
            task_id=generate_task_id(),
            user_request=user_request,
            input_path=image_path,
            status="pending",
            progress=0,
            metadata={},
            errors=[]
        )
        
        logger.info(f"Starting workflow for task {state.task_id}")
        
        # Chạy từng agent
        for agent in self.agents:
            logger.info(f"Running {agent.name}")
            state = await agent.process(state)
            
            # Nếu fail, dừng lại
            if state.status == "failed":
                logger.error(f"Workflow failed at {agent.name}: {state.errors}")
                break
        
        return state
```

## 5. Sử dụng trong FastAPI

```python
# Khởi tạo orchestrator
orchestrator = ImageProcessingOrchestrator()

@app.post("/api/v1/process")
async def process_image(
    file: UploadFile,
    request: str = Form(...),
    background_tasks: BackgroundTasks
):
    # Save file
    file_path = await save_uploaded_file(file)
    
    # Start background processing
    background_tasks.add_task(
        run_workflow, 
        request, 
        file_path
    )
    
    return {"task_id": task_id, "status": "pending"}

async def run_workflow(request: str, file_path: str):
    state = await orchestrator.run(request, file_path)
    
    # Update database
    tasks_db[state.task_id] = {
        "status": state.status,
        "progress": state.progress,
        "result_path": state.output_path,
        "errors": state.errors
    }
```

## 6. Improvements

### a) Add Decision Logic
```python
class RouterAgent(BaseAgent):
    """Quyết định agent nào sẽ chạy tiếp theo"""
    
    async def process(self, state: WorkflowState) -> str:
        if state.metadata.get("needs_retry"):
            return "retry_agent"
        elif state.task_type == "complex":
            return "advanced_worker"
        else:
            return "simple_worker"
```

### b) Add Memory
```python
class ConversationalAgent(BaseAgent):
    def __init__(self):
        self.memory = []  # Store conversation history
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        # Add to memory
        self.memory.append({
            "request": state.user_request,
            "response": state.output_path
        })
        
        # Use memory for context
        context = "\n".join([f"Q: {m['request']}" for m in self.memory[-3:]])
        # ... use context in LLM prompt
```

### c) Add Error Recovery
```python
class ResilientAgent(BaseAgent):
    async def process(self, state: WorkflowState) -> WorkflowState:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return await self._do_work(state)
            except Exception as e:
                if attempt == max_retries - 1:
                    state.status = "failed"
                    state.errors.append(str(e))
                else:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return state
```

## 7. Testing

```python
async def test_workflow():
    # Test individual agent
    analyzer = TaskAnalyzerAgent()
    state = WorkflowState(
        task_id="test_001",
        user_request="làm mờ nền",
        input_path="/path/to/image.jpg"
    )
    
    result = await analyzer.process(state)
    assert result.task_type == "inpaint"
    
    # Test full workflow
    orchestrator = ImageProcessingOrchestrator()
    final_state = await orchestrator.run("xóa object", "/path/to/image.jpg")
    
    assert final_state.status == "completed"
    assert final_state.output_path is not None
```

## 8. Key Takeaways

1. **State is King**: Tất cả agents chia sẻ state chung
2. **Single Responsibility**: Mỗi agent làm 1 việc duy nhất
3. **Error Handling**: Luôn handle errors và update state
4. **Logging**: Log mọi thứ để debug
5. **Async**: Dùng async/await cho performance
6. **Testing**: Test từng agent riêng lẻ trước

## 9. Next Steps

- Thêm LangGraph để visualize workflow
- Thêm streaming để user thấy progress real-time
- Thêm caching để tránh xử lý trùng
- Thêm monitoring (Prometheus, Grafana)
