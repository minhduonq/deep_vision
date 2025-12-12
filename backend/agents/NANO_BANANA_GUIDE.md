# 🍌 Nano Banana Agent - Hướng dẫn tích hợp

## Giới thiệu

**Nano Banana Agent** sử dụng model Google Nano Banana từ Replicate để thực hiện chỉnh sửa ảnh với AI. Agent này hoạt động song song với **Qwen Fast Edit Agent**, cung cấp thêm lựa chọn cho image editing tasks.

### Tính năng chính

- ✅ **Image Editing**: Chỉnh sửa ảnh theo prompt text
- ✅ **Multi-image Input**: Hỗ trợ chỉnh sửa với nhiều ảnh cùng lúc (tối đa 10 ảnh)
- ✅ **Style Transfer**: Chuyển đổi style ảnh
- ✅ **Beauty Enhancement**: Làm đẹp ảnh chân dung
- ✅ **Object Removal**: Xóa object không mong muốn
- ✅ **Aspect Ratio Control**: Điều chỉnh tỷ lệ khung hình
- ✅ **Async Processing**: Xử lý bất đồng bộ

## Cài đặt

### 1. Install dependencies

```bash
pip install replicate pillow
```

### 2. Cấu hình API token

```bash
# Linux/Mac
export REPLICATE_API_TOKEN="your_token_here"

# Windows PowerShell
$env:REPLICATE_API_TOKEN="your_token_here"
```

Hoặc khởi tạo agent với token:

```python
from nano_banana_agent import NanoBananaAgent

agent = NanoBananaAgent(api_token="your_token_here")
```

## Sử dụng cơ bản

### 1. Chỉnh sửa ảnh đơn giản

```python
import asyncio
from nano_banana_agent import nano_banana_agent

async def edit_example():
    result = await nano_banana_agent.edit_image(
        image_path="input.jpg",
        prompt="Make the scene more vibrant and colorful",
        output_dir="./outputs"
    )
    
    if result["success"]:
        print(f"Output saved to: {result['output_path']}")
    else:
        print(f"Error: {result['error']}")

asyncio.run(edit_example())
```

### 2. Chỉnh sửa với nhiều ảnh

```python
result = await nano_banana_agent.edit_image(
    image_path=["image1.jpg", "image2.jpg"],
    prompt="Make the sheets in the style of the logo. Make the scene natural.",
    output_dir="./outputs"
)
```

### 3. Style Transfer

```python
result = await nano_banana_agent.style_transfer(
    image_path="photo.jpg",
    style="anime art",
    output_dir="./outputs"
)
```

### 4. Beauty Enhancement

```python
result = await nano_banana_agent.beauty_enhance(
    image_path="portrait.jpg",
    level="natural",  # Options: "subtle", "natural", "strong"
    output_dir="./outputs"
)
```

### 5. Object Removal

```python
result = await nano_banana_agent.remove_object(
    image_path="photo.jpg",
    object_description="watermark",
    output_dir="./outputs"
)
```

## Tích hợp với Orchestrator

Agent cung cấp method `process_edit_request()` với interface tương tự Qwen Edit Agent để dễ dàng tích hợp:

```python
result = await nano_banana_agent.process_edit_request(
    image_path="input.jpg",
    prompt="Change the background to a beautiful sunset",
    output_dir="./outputs",
    aspect_ratio="16:9",
    output_format="jpg"
)
```

### Tích hợp vào chat_agent_routes.py

Để thêm Nano Banana như một lựa chọn cho editing tasks:

```python
# Option 1: Thay thế Qwen Edit
elif task_type == "edit":
    result = await nano_banana_agent.process_edit_request(
        image_path=str(input_path),
        prompt=prompt,
        output_dir=str(settings.OUTPUT_DIR)
    )

# Option 2: Cho user chọn agent
if user_preference == "nano_banana":
    result = await nano_banana_agent.process_edit_request(...)
else:
    result = await qwen_fast_edit_agent.edit_image(...)
```

## API Parameters

### `edit_image()`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_path` | `str` hoặc `List[str]` | Required | Đường dẫn ảnh input |
| `prompt` | `str` | Required | Mô tả cách chỉnh sửa |
| `aspect_ratio` | `str` | `"match_input_image"` | Tỷ lệ khung hình: `"1:1"`, `"16:9"`, `"9:16"`, `"4:3"`, `"3:4"` |
| `output_format` | `str` | `"jpg"` | Format output: `"jpg"` hoặc `"png"` |
| `output_dir` | `str` | `None` | Thư mục lưu kết quả (nếu None, trả về URL) |

### Aspect Ratio Options

- `match_input_image` - Giữ nguyên tỷ lệ ảnh gốc
- `1:1` - Hình vuông
- `16:9` - Landscape wide
- `9:16` - Portrait tall
- `4:3` - Standard landscape
- `3:4` - Standard portrait
- `21:9` - Ultra-wide
- `9:21` - Ultra-tall

## So sánh với Qwen Fast Edit

| Feature | Nano Banana | Qwen Fast Edit |
|---------|-------------|----------------|
| **Multi-image input** | ✅ (tối đa 10) | ❌ (1 ảnh) |
| **Aspect ratio control** | ✅ | ❌ |
| **Speed** | Trung bình | Nhanh hơn |
| **Quality** | Cao | Rất cao |
| **API Platform** | Replicate | HuggingFace/Custom |
| **Cost** | Pay-per-use | Free (self-hosted) |

## Testing

Chạy test script:

```bash
cd backend/agents
python test_nano_banana.py
```

Nhớ update `TEST_IMAGE` path trong test script trước khi chạy.

## Output Format

Kết quả trả về:

```python
{
    "success": True,
    "output_path": "/path/to/output.jpg",
    "num_images": 1,
    "metadata": {
        "prompt": "Your prompt here",
        "aspect_ratio": "16:9",
        "output_format": "jpg",
        "model": "Google Nano Banana",
        "model_version": "google/nano-banana"
    }
}
```

## Best Practices

### 1. Prompt Engineering

**Good prompts:**
- "Change the background to a beach sunset scene"
- "Make the person wearing a red dress instead of blue"
- "Transform into anime art style with vibrant colors"

**Avoid:**
- Quá ngắn: "change color"
- Quá chung chung: "make it better"
- Thiếu context: "add object"

### 2. Performance Tips

- Sử dụng `output_format="jpg"` cho ảnh thông thường (nhẹ hơn)
- Sử dụng `output_format="png"` khi cần quality cao hoặc transparency
- Với multi-image input, giới hạn số lượng ảnh để tránh timeout
- Implement rate limiting khi xử lý nhiều requests

### 3. Error Handling

```python
try:
    result = await nano_banana_agent.edit_image(...)
    
    if not result["success"]:
        logger.error(f"Edit failed: {result.get('error')}")
        # Fallback to alternative method
        result = await qwen_fast_edit_agent.edit_image(...)
        
except Exception as e:
    logger.error(f"Exception: {e}")
    # Handle exception
```

## Roadmap

- [ ] Add batch processing với queue system
- [ ] Implement caching cho repeated prompts
- [ ] Add progress callback cho long-running tasks
- [ ] Support cho video editing
- [ ] Integration với frontend UI cho agent selection

## Links

- **Replicate Model**: https://replicate.com/google/nano-banana
- **API Documentation**: https://replicate.com/google/nano-banana/api
- **GitHub Repository**: [Your repo link]

## Troubleshooting

### Error: "REPLICATE_API_TOKEN not set"

Set environment variable:
```bash
export REPLICATE_API_TOKEN="r8_..."
```

### Error: "Input file not found"

Kiểm tra đường dẫn file tồn tại:
```python
from pathlib import Path
assert Path(image_path).exists(), f"File not found: {image_path}"
```

### Error: "Rate limit exceeded"

Thêm delay giữa các requests:
```python
await asyncio.sleep(2)  # Wait 2 seconds between calls
```

### Output quality không như mong đợi

- Cải thiện prompt (cụ thể hơn, chi tiết hơn)
- Thử với `aspect_ratio` khác nhau
- Dùng `output_format="png"` cho quality cao hơn

## License

MIT License - See LICENSE file for details

---

**Made with 💙 by Deep Vision Team**
