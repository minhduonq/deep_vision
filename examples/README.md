# Examples - Multi-Agent System

Các ví dụ thực tế về cách sử dụng hệ thống multi-agent.

## Files

### 1. `agent_usage_example.py`
Ví dụ cơ bản về cách sử dụng các agents:
- Simple workflow
- LLM-based task analyzer
- Rule-based analyzer
- Individual agent usage
- Error handling

**Chạy:**
```bash
python examples/agent_usage_example.py
```

## Quick Start

### Example 1: Xử lý ảnh với task được chỉ định sẵn

```python
from backend.core.state import WorkflowState, TaskType
from backend.agents.orchestrator import SimpleOrchestrator

# Tạo state
state = WorkflowState(
    task_id="task_001",
    user_request="Làm rõ ảnh",
    task_type=TaskType.DEBLUR,  # Chỉ định task
    input_path="path/to/image.jpg"
)

# Chạy workflow (không dùng LLM analyzer)
orchestrator = SimpleOrchestrator(use_llm_analyzer=False)
result = await orchestrator.run(state)

print(f"Status: {result.status.value}")
print(f"Output: {result.output_path}")
```

### Example 2: Để LLM phân tích request

```python
# KHÔNG chỉ định task_type, để LLM quyết định
state = WorkflowState(
    task_id="task_002",
    user_request="Xóa người ở phía sau",  # Ambiguous
    input_path="path/to/image.jpg"
)

# Dùng LLM analyzer
orchestrator = SimpleOrchestrator(use_llm_analyzer=True)
result = await orchestrator.run(state)

# LLM sẽ phân tích và chọn task_type phù hợp
print(f"LLM detected: {result.task_type.value}")
print(f"Confidence: {result.intermediate_results['analysis']['confidence']}")
```

### Example 3: Rule-based (không cần OpenAI)

```python
from backend.agents.task_analyzer import SimpleTaskAnalyzer

analyzer = SimpleTaskAnalyzer()
result = await analyzer.analyze("Làm rõ ảnh mờ")

print(f"Task: {result['task_type']}")
print(f"Confidence: {result['confidence']}")
```

### Example 4: Sử dụng agents riêng lẻ

```python
from backend.agents.task_analyzer import TaskAnalyzerAgent
from backend.agents.image_worker import ImageWorkerAgent
from backend.agents.quality_control import QualityControlAgent

# Chỉ dùng Task Analyzer
analyzer = TaskAnalyzerAgent()
state = await analyzer.process(state)

# Chỉ dùng Worker
worker = ImageWorkerAgent()
state = await worker.process(state)

# Chỉ dùng Quality Control
qc = QualityControlAgent()
state = await qc.process(state)
```

## Architecture

```
User Request → TaskAnalyzer → ImageWorker → QualityControl → Result
```

### Agents

1. **TaskAnalyzerAgent** (LLM-based)
   - Phân tích yêu cầu user bằng GPT-4
   - Xác định task_type và confidence
   - Output: Updated state with task_type

2. **SimpleTaskAnalyzer** (Rule-based)
   - Phân tích bằng keywords
   - Không cần API key
   - Nhanh nhưng kém chính xác

3. **ImageWorkerAgent**
   - Gọi Replicate API
   - Xử lý ảnh theo task_type
   - Output: Processed image path

4. **QualityControlAgent**
   - Kiểm tra output
   - Validate file size, format, dimensions
   - Output: Pass/Fail status

## State Flow

```python
WorkflowState:
    task_id: str
    user_request: str
    task_type: TaskType
    status: TaskStatus
    progress: int (0-100)
    input_path: str
    output_path: str
    intermediate_results: dict
```

State được truyền qua các agents:
1. Initial state
2. Analyzer updates: task_type, analysis
3. Worker updates: output_path, model_used
4. QC updates: quality_checks, final status

## Tips

1. **Development**: Dùng `use_llm_analyzer=False` để tiết kiệm API calls
2. **Production**: Dùng `use_llm_analyzer=True` cho accuracy cao
3. **Error Handling**: Luôn check `state.status` và `state.intermediate_results['errors']`
4. **Logging**: Agents tự động log, check logs để debug
5. **Testing**: Test từng agent riêng trước khi test full workflow

## Testing

```bash
# Test individual agents
pytest tests/test_agents.py

# Test orchestrator
pytest tests/test_orchestrator.py

# Run examples
python examples/agent_usage_example.py
```
