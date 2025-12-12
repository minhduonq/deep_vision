# 🚀 Hướng Dẫn Chạy Deep Vision

## ✅ Trạng Thái Hiện Tại

### Backend (FastAPI)
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Status**: ✅ Running
- **Health Check**: http://localhost:8000/api/v1/health

### Frontend (React + Vite)
- **URL**: http://localhost:5173
- **Status**: ✅ Running

## 📦 Các Agent Đã Tích Hợp

### 1. **Qwen Edit Agent** (Standard & Fast)
- Chỉnh sửa ảnh theo prompt
- Hỗ trợ đến 10 ảnh cùng lúc
- Deblur, remove object, beauty enhance, style transfer
- File: `backend/agents/qwen_edit_agent.py`

### 2. **Nano Banana Agent** (Google Replicate)
- Agent dự phòng khi Qwen không khả dụng
- Tích hợp Replicate API
- Hỗ trợ đến 10 ảnh cùng lúc
- File: `backend/agents/nano_banana_agent.py`

### 3. **HuggingFace Generation Agent**
- Tạo ảnh từ text prompt
- Sử dụng Z-Image-Turbo model
- File: `backend/agents/huggingface_generation_agent.py`

### 4. **Replicate Wrapper**
- Deblur, inpainting, beauty enhancement
- File: `backend/models/replicate_wrapper.py`

## 🎯 API Endpoints

### Image Enhancement
```bash
POST /api/v1/enhance
- task_type: deblur | inpaint | beauty_enhance
- file: image file
- description: optional description
```

### Image Generation
```bash
POST /api/v1/generate
{
  "prompt": "A beautiful landscape",
  "width": 512,
  "height": 512,
  "steps": 30,
  "guidance": 7.5
}
```

### Task Status
```bash
GET /api/v1/status/{task_id}
```

### Get Result
```bash
GET /api/v1/result/{task_id}
```

## 🧪 Test API với PowerShell

### 1. Health Check
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/health' -Method Get
```

### 2. Generate Image
```powershell
$body = @{
    prompt = "A beautiful sunset over mountains"
    width = 512
    height = 512
    steps = 30
    guidance = 7.5
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/generate' -Method Post -Body $body -ContentType 'application/json'
$response
```

### 3. Check Task Status
```powershell
$taskId = $response.task_id
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/status/$taskId" -Method Get
```

### 4. Upload Image for Enhancement
```powershell
$filePath = "path\to\your\image.jpg"
$form = @{
    file = Get-Item -Path $filePath
    task_type = "deblur"
    description = "Sharpen this image"
}

$response = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/enhance' -Method Post -Form $form
$response
```

## 🌐 Sử Dụng Frontend

1. Mở trình duyệt: **http://localhost:5173**
2. Chọn tính năng:
   - **Generation**: Tạo ảnh từ text
   - **Enhancement**: Làm sắc nét, xóa object, làm đẹp
   - **History**: Xem lịch sử xử lý

## 🔑 API Keys Cần Thiết

### Replicate API (Bắt buộc cho Nano Banana)
```bash
# Trong file .env
REPLICATE_API_TOKEN=your_token_here
```
Lấy tại: https://replicate.com/account/api-tokens

### HuggingFace Token (Optional)
```bash
HUGGINGFACE_API_TOKEN=your_token_here
```

## 📁 Cấu Trúc Thư Mục

```
deep_vision/
├── backend/
│   ├── agents/
│   │   ├── qwen_edit_agent.py          # Qwen cho editing
│   │   ├── nano_banana_agent.py        # Nano Banana backup
│   │   ├── huggingface_generation_agent.py
│   │   └── edit_manager.py             # Manager với fallback
│   ├── api/
│   │   └── main.py                     # FastAPI server
│   └── models/
│       └── replicate_wrapper.py
├── frontend-react/
│   ├── src/
│   │   ├── api/client.ts               # API client
│   │   ├── pages/
│   │   └── components/
│   └── .env
└── .env
```

## 🛠️ Troubleshooting

### Backend không start
```bash
# Activate environment
conda activate deepvision

# Install dependencies
pip install uvicorn fastapi python-multipart aiofiles loguru openai replicate pydantic-settings gradio-client
```

### Frontend không start
```bash
cd frontend-react
npm install
npm run dev
```

### CORS Error
Kiểm tra file `.env` backend:
```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8501,http://localhost:8000
```

