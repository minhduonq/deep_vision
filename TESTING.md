# Testing Deep Vision API

## 🎯 Hệ thống đang chạy

Bạn đã có cả backend và frontend đang chạy:

- ✅ **Backend API**: http://localhost:8000
- ✅ **API Docs**: http://localhost:8000/docs
- ✅ **Frontend**: http://localhost:8501

## 🧪 Test API với Swagger UI

### 1. Mở Swagger UI
Truy cập: http://localhost:8000/docs

### 2. Test Health Check
1. Click vào `GET /api/v1/health`
2. Click "Try it out"
3. Click "Execute"
4. Xem response - should see:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "gpu_available": true/false,
  "device": "cuda",
  "active_tasks": 0,
  "total_tasks": 0
}
```

### 3. Test Root Endpoint
1. Click vào `GET /`
2. Click "Try it out"
3. Click "Execute"
4. Should see:
```json
{
  "name": "DeepVision",
  "version": "0.1.0",
  "status": "running",
  "docs": "/docs"
}
```

## 🎨 Test Frontend với Streamlit

### 1. Mở Streamlit
Truy cập: http://localhost:8501

### 2. Test Image Enhancement
1. Chọn mode: "Image Enhancement"
2. Chọn enhancement type (Deblur, Remove Object, hoặc Beauty Enhancement)
3. Upload một ảnh test
4. Click "Process Image"
5. Hiện tại sẽ thấy message "Feature coming soon!" (vì chưa implement agents)

### 3. Test Image Generation
1. Chọn mode: "Image Generation"
2. Nhập prompt (ví dụ: "a beautiful sunset over mountains")
3. Click "Generate"
4. Hiện tại sẽ thấy message "Feature coming soon!"

## 🔧 Test API với PowerShell

Mở terminal PowerShell mới và test:

### Test Root
```powershell
Invoke-RestMethod http://localhost:8000/
```

### Test Health Check
```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
```

### Test Upload Image (Mock)
```powershell
# Tạo test image (nếu có)
$file = Get-Item "path/to/test_image.jpg"
$form = @{
    file = $file
    task_type = "deblur"
    description = "Make this image sharper"
}

Invoke-RestMethod -Uri http://localhost:8000/api/v1/enhance `
    -Method Post `
    -Form $form
```

Kết quả sẽ trả về:
```json
{
  "task_id": "task_xxxxx",
  "status": "pending",
  "message": "Enhancement task created successfully. Task type: deblur",
  "estimated_time": 30
}
```

## 📊 Kiểm tra Logs

Backend sẽ log tất cả requests:

```
2025-11-19 21:XX:XX | INFO | main:health_check - Health check called
2025-11-19 21:XX:XX | INFO | main:enhance_image - Received enhancement request: deblur
```

Logs được lưu tại:
- Console output
- `logs/app_*.log` files

## ⚠️ Current Limitations

Hiện tại chỉ có **infrastructure sẵn sàng**, chưa có actual processing:

❌ **Chưa implement:**
- Task Analyzer Agent
- Model wrappers (Replicate API)
- Enhancement agents
- Generation agents
- Actual image processing

✅ **Đã có:**
- FastAPI backend hoàn chỉnh
- All endpoints defined
- State management
- Configuration system
- Frontend UI
- File upload/download structure

## 🚀 Next Steps - Implement Agents

### Step 1: Get API Keys

**Required:**
```powershell
# Mở .env file
notepad .env

# Thêm API keys:
OPENAI_API_KEY=sk-...
REPLICATE_API_TOKEN=r8_...
```

**Lấy API keys tại:**
- OpenAI: https://platform.openai.com/api-keys
- Replicate: https://replicate.com/account/api-tokens

### Step 2: Implement Task Analyzer

Tạo file `backend/agents/task_analyzer.py`:

```python
from langchain_openai import ChatOpenAI
from backend.core.state import WorkflowState, TaskType
from backend.core.config import settings

class TaskAnalyzerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
    
    async def analyze(self, state: WorkflowState) -> WorkflowState:
        # Implement analysis logic
        pass
```

### Step 3: Implement Replicate Wrapper

Tạo file `backend/models/replicate_wrapper.py`:

```python
import replicate
from backend.core.config import settings

class ReplicateWrapper:
    def __init__(self):
        self.client = replicate.Client(
            api_token=settings.REPLICATE_API_TOKEN
        )
    
    async def deblur_image(self, image_path: str):
        # Implement deblur
        pass
```

### Step 4: Connect to API

Update `backend/api/main.py` để sử dụng agents:

```python
from backend.agents.task_analyzer import task_analyzer
from backend.agents.enhancement_agent import enhancement_agent

async def process_enhancement_task(task_id: str):
    # Get task
    task = tasks_db[task_id]
    
    # Create state
    state = WorkflowState(...)
    
    # Analyze
    state = await task_analyzer.analyze(state)
    
    # Process
    state = await enhancement_agent.process(state)
    
    # Update task
    tasks_db[task_id]["status"] = "completed"
```

## 📖 Detailed Implementation Guide

Xem file **IMPLEMENTATION.md** cho hướng dẫn chi tiết từng bước.

## ✅ Quick Verification Checklist

- [ ] Backend running at http://localhost:8000
- [ ] Swagger docs accessible at http://localhost:8000/docs
- [ ] Health check returns status "healthy"
- [ ] Frontend running at http://localhost:8501
- [ ] Can upload image in frontend
- [ ] Can see "Feature coming soon" messages
- [ ] Logs showing in console
- [ ] Ready to implement agents

## 🎉 Current Status

**Infrastructure: 100% Complete** ✅  
**Agent Implementation: 0% Complete** ⏳  
**Overall Progress: ~20%** 📊

Bạn đã sẵn sàng để bắt đầu implement agents!

## 💡 Recommended Next Action

1. **Lấy API keys** (OpenAI + Replicate)
2. **Đọc IMPLEMENTATION.md** 
3. **Implement Task Analyzer** (first agent)
4. **Test end-to-end** với một ảnh thật
5. **Iterate and expand**

Good luck! 🚀
