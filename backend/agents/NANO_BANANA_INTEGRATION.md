# 🍌 Nano Banana Agent Integration Summary

## ✅ Đã hoàn thành

### 1. **Core Agent Implementation**
   - ✅ File: `backend/agents/nano_banana_agent.py`
   - ✅ Cập nhật API theo documentation chính thức của Google Nano Banana
   - ✅ Sử dụng `replicate.run("google/nano-banana", input={...})`
   - ✅ Hỗ trợ single và multiple image inputs (tối đa 10 ảnh)
   - ✅ Aspect ratio control: "match_input_image", "1:1", "16:9", "9:16", etc.
   - ✅ Output format: JPG hoặc PNG

### 2. **Key Features**
   ```python
   # Main method
   await nano_banana_agent.edit_image(
       image_path="input.jpg",  # hoặc list ["img1.jpg", "img2.jpg"]
       prompt="Make the scene more vibrant",
       aspect_ratio="16:9",
       output_format="jpg",
       output_dir="./outputs"
   )
   
   # Helper methods
   await nano_banana_agent.style_transfer(image_path, style="anime")
   await nano_banana_agent.beauty_enhance(image_path, level="natural")
   await nano_banana_agent.remove_object(image_path, object_description="watermark")
   await nano_banana_agent.deblur(image_path, strength="medium")
   
   # Orchestrator integration
   await nano_banana_agent.process_edit_request(
       image_path="input.jpg",
       prompt="Edit instruction",
       output_dir="./outputs"
   )
   ```

### 3. **Documentation**
   - ✅ File: `backend/agents/NANO_BANANA_GUIDE.md`
   - ✅ Chi tiết usage examples
   - ✅ API parameters reference
   - ✅ Integration guide
   - ✅ Best practices & troubleshooting
   - ✅ So sánh với Qwen Fast Edit

### 4. **Testing**
   - ✅ File: `backend/agents/test_nano_banana.py`
   - ✅ Test cases cho các features chính
   - ✅ Error handling examples

## 🎯 API Format (theo documentation)

```python
output = replicate.run(
    "google/nano-banana",
    input={
        "prompt": "Make the sheets in the style of the logo",
        "image_input": [file_handle1, file_handle2],  # hoặc URLs
        "aspect_ratio": "match_input_image",
        "output_format": "jpg"
    }
)

# Access output
output_url = output.url()
# Or save to disk
with open("output.jpg", "wb") as f:
    f.write(output.read())
```

## 📊 So sánh với Qwen Fast Edit

| Aspect | Nano Banana | Qwen Fast Edit |
|--------|-------------|----------------|
| **Input** | 1-10 ảnh | 1 ảnh |
| **Platform** | Replicate (cloud) | HuggingFace/Self-hosted |
| **Speed** | Trung bình (~10-20s) | Nhanh (~5-10s) |
| **Quality** | Rất tốt | Xuất sắc |
| **Aspect Ratio** | Flexible | Fixed |
| **Cost** | Pay-per-use | Free (self-hosted) |
| **Multi-image** | ✅ | ❌ |

## 🔧 Cách tích hợp vào hệ thống

### Option 1: Thay thế hoàn toàn Qwen Edit

```python
# Trong chat_agent_routes.py, line ~296
elif task_type == "edit":
    # Thay vì:
    # result = await qwen_fast_edit_agent.edit_image(...)
    
    # Dùng:
    result = await nano_banana_agent.process_edit_request(
        image_path=str(input_path),
        prompt=prompt,
        output_dir=str(settings.OUTPUT_DIR)
    )
```

### Option 2: Cho phép user chọn agent

```python
# Thêm parameter vào ChatRequest
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    image: Optional[UploadFile] = None
    edit_agent: str = "qwen"  # "qwen" hoặc "nano_banana"

# Trong process_enhancement_task
if task_type == "edit":
    if edit_agent == "nano_banana":
        result = await nano_banana_agent.process_edit_request(...)
    else:
        result = await qwen_fast_edit_agent.edit_image(...)
```

### Option 3: Hybrid approach - Dùng cả hai

```python
# Dùng Nano Banana cho multi-image editing
if isinstance(image_path, list) and len(image_path) > 1:
    result = await nano_banana_agent.process_edit_request(...)
else:
    # Dùng Qwen cho single image (nhanh hơn)
    result = await qwen_fast_edit_agent.edit_image(...)
```

### Option 4: Fallback mechanism

```python
try:
    # Try Qwen first (faster)
    result = await qwen_fast_edit_agent.edit_image(...)
    
    if not result.get("success"):
        # Fallback to Nano Banana
        logger.warning("Qwen failed, falling back to Nano Banana")
        result = await nano_banana_agent.process_edit_request(...)
        
except Exception as e:
    logger.error(f"Qwen error: {e}, trying Nano Banana")
    result = await nano_banana_agent.process_edit_request(...)
```

## 🚀 Các bước để deploy

### 1. Cài đặt dependencies
```bash
pip install replicate pillow
```

### 2. Set REPLICATE_API_TOKEN
```bash
# Add to .env
REPLICATE_API_TOKEN=r8_your_token_here

# Hoặc trong code
import os
os.environ["REPLICATE_API_TOKEN"] = "r8_your_token_here"
```

### 3. Test agent
```bash
cd backend/agents
python test_nano_banana.py
```

### 4. Cập nhật orchestrator (nếu cần)
```python
# Trong orchestrator.py hoặc chat_agent_routes.py
from backend.agents.nano_banana_agent import nano_banana_agent

# Sử dụng như đã mô tả ở Option 1-4 trên
```

### 5. Update frontend (nếu muốn user chọn agent)
```typescript
// Trong Generation.tsx hoặc Home.tsx
<select name="editAgent">
  <option value="qwen">Qwen Fast Edit (Nhanh)</option>
  <option value="nano_banana">Nano Banana (Multi-image)</option>
</select>
```

## 📝 Usage Examples

### Example 1: Chỉnh sửa ảnh cơ bản
```python
result = await nano_banana_agent.edit_image(
    image_path="photo.jpg",
    prompt="Make the sky more dramatic with sunset colors",
    output_dir="./outputs"
)
```

### Example 2: Multi-image composition
```python
result = await nano_banana_agent.edit_image(
    image_path=["product.jpg", "logo.png"],
    prompt="Blend the logo onto the product naturally",
    aspect_ratio="1:1",
    output_dir="./outputs"
)
```

### Example 3: Style transfer
```python
result = await nano_banana_agent.style_transfer(
    image_path="portrait.jpg",
    style="oil painting, Renaissance style",
    output_dir="./outputs"
)
```

## ⚠️ Important Notes

1. **Rate Limiting**: Replicate có rate limits, cần implement delay giữa requests
2. **Cost**: Nano Banana là paid service trên Replicate (check pricing)
3. **Async**: Tất cả methods đều async, nhớ `await`
4. **File Handles**: Agent tự động xử lý file I/O, có thể pass URL hoặc local path
5. **Error Handling**: Luôn check `result["success"]` trước khi dùng output

## 🎨 Khi nào nên dùng Nano Banana?

**Dùng Nano Banana khi:**
- ✅ Cần chỉnh sửa với nhiều ảnh cùng lúc (blend, composite)
- ✅ Cần control aspect ratio cụ thể
- ✅ Qwen Edit không cho kết quả tốt
- ✅ Cần style transfer phức tạp

**Dùng Qwen Fast Edit khi:**
- ✅ Chỉ cần edit 1 ảnh đơn giản
- ✅ Cần tốc độ xử lý nhanh
- ✅ Muốn giảm cost (free/self-hosted)
- ✅ Không cần multi-image support

## 📚 Additional Resources

- **API Docs**: https://replicate.com/google/nano-banana/api
- **Examples**: https://replicate.com/google/nano-banana/examples
- **Pricing**: https://replicate.com/pricing

---

**Status**: ✅ Ready for integration
**Last Updated**: 2025-01-11
**Maintainer**: Deep Vision Team
