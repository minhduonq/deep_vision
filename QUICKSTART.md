# Deep Vision - Quick Start Guide

## 🚀 Bắt đầu nhanh (Quick Start)

Hướng dẫn này giúp bạn setup và chạy Deep Vision project nhanh nhất có thể.

## Yêu cầu hệ thống (Prerequisites)

- **Python**: 3.10 hoặc cao hơn
- **GPU**: NVIDIA GPU với CUDA (tùy chọn, nhưng khuyến nghị)
- **RAM**: Tối thiểu 8GB (khuyến nghị 16GB)
- **Storage**: ~20GB cho models và dependencies

## Bước 1: Clone và Setup Environment

```powershell
# Tạo virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# Hoặc nếu bị lỗi execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip
```

## Bước 2: Cài đặt Dependencies

### Cách 1: GPU Setup (khuyến nghị nếu có NVIDIA GPU)

```powershell
# Cài PyTorch với CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Cài các packages còn lại
pip install -r requirements.txt
```

### Cách 2: CPU-Only Setup

```powershell
# Sửa trong requirements.txt:
# torch==2.1.2 thành torch==2.1.2+cpu
# torchvision==0.16.2 thành torchvision==0.16.2+cpu

pip install -r requirements.txt
```

### Cách 3: API-Only (không cần GPU mạnh)

```powershell
# Chỉ cài dependencies cơ bản
pip install fastapi uvicorn python-multipart pydantic
pip install langchain langgraph langchain-openai
pip install opencv-python pillow numpy
pip install replicate httpx streamlit
```

## Bước 3: Cấu hình Environment Variables

```powershell
# Copy file .env.example
copy .env.example .env

# Mở .env và điền API keys của bạn
notepad .env
```

**Cần thiết phải có:**
- `OPENAI_API_KEY` hoặc `ANTHROPIC_API_KEY` (cho LLM agents)

**Tùy chọn (nếu dùng API thay vì local models):**
- `REPLICATE_API_TOKEN` (khuyến nghị - dễ setup nhất)
- `STABILITY_API_KEY` (cho Stable Diffusion)
- `HUGGINGFACE_API_TOKEN` (cho HF models)

## Bước 4: Tạo cấu trúc thư mục

```powershell
# Tạo các thư mục cần thiết
New-Item -ItemType Directory -Force -Path backend,backend\api,backend\agents,backend\models,backend\core,frontend,uploads,outputs,models,logs
```

## Bước 5: Tạo Backend cơ bản

Tạo file `backend/api/main.py`:

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
from pathlib import Path

app = FastAPI(title="Deep Vision API", version="0.1.0")

# Tạo thư mục nếu chưa có
Path("uploads").mkdir(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Deep Vision API is running!", "version": "0.1.0"}

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "gpu_available": False,  # TODO: implement GPU check
        "models_loaded": []
    }

@app.post("/api/v1/enhance")
async def enhance_image(file: UploadFile = File(...)):
    """Endpoint để xử lý enhancement tasks"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # TODO: Implement enhancement logic
    return {
        "task_id": "temp_123",
        "status": "processing",
        "message": "Enhancement task created"
    }

@app.post("/api/v1/generate")
async def generate_image(prompt: str):
    """Endpoint để generate ảnh từ prompt"""
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    # TODO: Implement generation logic
    return {
        "task_id": "temp_456",
        "status": "processing",
        "message": "Generation task created"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

## Bước 6: Chạy Backend

```powershell
# Cách 1: Chạy trực tiếp (code đã sửa để support)
python backend/api/main.py

# Cách 2: Dùng module syntax (khuyến nghị)
python -m backend.api.main

# Cách 3: Dùng uvicorn trực tiếp
uvicorn backend.api.main:app --reload
```

Mở browser và truy cập:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Bước 7: Tạo Frontend đơn giản (Streamlit)

Tạo file `frontend/streamlit_app.py`:

```python
import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Deep Vision", page_icon="🎨", layout="wide")

st.title("🎨 Deep Vision - AI Image Processing")

API_BASE_URL = "http://localhost:8000/api/v1"

# Sidebar
st.sidebar.header("Options")
task_type = st.sidebar.selectbox(
    "Select Task",
    ["Image Enhancement", "Image Generation"]
)

if task_type == "Image Enhancement":
    st.header("📸 Image Enhancement")
    
    enhancement_type = st.selectbox(
        "Enhancement Type",
        ["Deblur", "Remove Object", "Beauty Enhancement"]
    )
    
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
        
        with col2:
            st.subheader("Enhanced Image")
            if st.button("Process Image"):
                with st.spinner("Processing..."):
                    # TODO: Call API
                    st.info("Feature coming soon!")

else:  # Image Generation
    st.header("🎨 Image Generation")
    
    prompt = st.text_area("Enter your prompt", height=100)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        negative_prompt = st.text_input("Negative prompt (optional)")
        num_images = st.slider("Number of images", 1, 4, 1)
    
    if st.button("Generate Image"):
        if prompt:
            with st.spinner("Generating..."):
                # TODO: Call API
                st.info("Feature coming soon!")
        else:
            st.warning("Please enter a prompt")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Deep Vision v0.1.0")
```

## Bước 8: Chạy Frontend

```powershell
# Mở terminal mới (giữ backend đang chạy)
streamlit run frontend/streamlit_app.py
```

Mở browser và truy cập: http://localhost:8501

## 🎯 Chiến lược triển khai theo giai đoạn

### Giai đoạn 1: API-First (Tuần 1) - KHUYẾN NGHỊ BẮT ĐẦU TẠI ĐÂY

**Ưu điểm:**
- Không cần GPU mạnh
- Chi phí thấp (pay-as-you-go)
- Deploy nhanh
- Tập trung vào logic agents

**Setup:**
```python
# Sử dụng Replicate API cho tất cả models
import replicate

# Deblur
output = replicate.run(
    "jingyunliang/swinir:...",
    input={"image": image_url}
)

# Generation
output = replicate.run(
    "stability-ai/sdxl:...",
    input={"prompt": prompt}
)
```

### Giai đoạn 2: Hybrid (Tuần 2-3)

**Khi nào chuyển:**
- Khi có nhiều users
- Chi phí API cao
- Cần tùy chỉnh models

**Setup:**
```python
# Lightweight models → local
# Heavy models → API

if model_size < threshold:
    result = local_inference(image)
else:
    result = api_inference(image)
```

### Giai đoạn 3: Full Local (Tuần 4+)

**Khi nào chuyển:**
- Có GPU tốt (RTX 3060+)
- Traffic ổn định
- Cần privacy/offline

## ⚡ Optimization Tips cho GPU hạn chế

### 1. Sử dụng Model nhỏ gọn

```python
# Thay vì SD 1.5 hoặc SDXL
model = "stabilityai/stable-diffusion-2-1-base"  # Nhẹ hơn

# Hoặc dùng LCM cho faster inference
from diffusers import LCMScheduler
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
```

### 2. Giảm resolution

```python
# Trong .env
DEFAULT_IMAGE_SIZE=512  # Thay vì 1024
MAX_IMAGE_SIZE=768
```

### 3. Enable optimizations

```python
import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,  # Giảm 50% VRAM
    use_safetensors=True
)

# Memory optimizations
pipe.enable_attention_slicing()  # Giảm VRAM usage
pipe.enable_vae_slicing()
if torch.cuda.is_available():
    pipe.enable_xformers_memory_efficient_attention()
```

### 4. Offload to CPU

```python
# Sequential CPU offload (tiết kiệm VRAM nhất nhưng chậm hơn)
pipe.enable_sequential_cpu_offload()

# Model CPU offload (cân bằng)
pipe.enable_model_cpu_offload()
```

## 📊 So sánh các approach

| Approach | GPU Requirement | Cost | Speed | Customization |
|----------|----------------|------|-------|---------------|
| **API-Only** | None | Medium | Fast | Low |
| **Hybrid** | 4GB VRAM | Low-Medium | Medium | Medium |
| **Full Local** | 8GB+ VRAM | Low | Slow-Medium | High |

## 🐛 Troubleshooting

### Lỗi CUDA Out of Memory

```python
# Giảm batch size
MAX_BATCH_SIZE=1

# Giảm resolution
image = image.resize((512, 512))

# Clear cache
import torch
torch.cuda.empty_cache()
```

### Lỗi Import

```powershell
# Reinstall với --force
pip install --force-reinstall transformers diffusers
```

### Lỗi PowerShell Execution Policy

```powershell
# Run as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📝 Next Steps

1. ✅ **Setup xong môi trường** → Chạy thử basic API
2. 🔑 **Lấy API keys** → OpenAI/Anthropic (cho agents), Replicate (cho models)
3. 🤖 **Implement agents** → Bắt đầu với Task Analyzer
4. 🎨 **Tích hợp first model** → Chọn 1 task (deblur hoặc generation)
5. 🧪 **Test end-to-end** → Từ upload ảnh đến nhận kết quả
6. 🎯 **Expand features** → Thêm các tasks khác
7. 🚀 **Optimize** → Based on usage patterns

## 💡 Khuyến nghị của tôi

**Cho bạn (GPU hạn chế):**

1. **Week 1-2**: Dùng 100% API
   - Focus vào logic agents và workflow
   - Dùng Replicate cho tất cả CV tasks
   - Dùng OpenAI/Anthropic cho LLM agents

2. **Week 3**: Test hybrid
   - Chạy preprocessing (resize, format conversion) local
   - Heavy inference qua API

3. **Week 4+**: Quyết định dựa trên:
   - Số lượng users
   - Chi phí API
   - GPU availability

**Start simple, scale smart! 🚀**

## 🆘 Cần hỗ trợ?

- Đọc `ARCHITECTURE.md` cho technical details
- Check `README.md` cho overview
- Xem examples trong `examples/` folder (coming soon)

Good luck! 🎉
