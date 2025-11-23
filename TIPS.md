# 💡 Tips & Best Practices

## Những tips quan trọng khi xây dựng Deep Vision

---

## 🎯 Development Tips

### 1. Start với API-First Approach

**Tại sao:**
- Không cần GPU ngay từ đầu
- Focus vào business logic và agents
- Dễ test và iterate
- Chi phí thấp ban đầu

**Khi nào chuyển sang local:**
- Khi traffic ổn định
- Chi phí API cao
- Cần customization cao
- Có GPU phù hợp

### 2. Test Incremental, Don't Wait

```python
# ❌ Không tốt
def process_everything():
    analyze()
    enhance()
    quality_check()
    save()
    # Test tất cả cùng lúc

# ✅ Tốt hơn
def test_each_step():
    # Test analyze
    result = analyze()
    assert result is not None
    
    # Test enhance
    result = enhance()
    assert result is not None
    
    # ...
```

### 3. Log Everything (But Wisely)

```python
# ✅ Good logging
logger.info(f"Processing task {task_id}")
logger.debug(f"Parameters: {params}")
logger.error(f"Error in {function_name}: {error}")

# ❌ Too much
logger.debug(f"Variable x = {x}")  # Every variable
logger.info("Starting function")   # Obvious things

# ❌ Too little
# No logging at all
```

### 4. Handle Errors Gracefully

```python
# ✅ Good error handling
try:
    result = process_image()
except APIError as e:
    logger.error(f"API error: {e}")
    return {"error": "External service unavailable", "retry": True}
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    return {"error": "Invalid input parameters", "retry": False}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"error": "Internal error", "retry": True}
```

### 5. Use Type Hints

```python
# ✅ Clear and maintainable
def process_image(
    image_path: str,
    task_type: TaskType,
    parameters: Dict[str, Any]
) -> Optional[str]:
    pass

# ❌ Hard to understand
def process_image(image_path, task_type, parameters):
    pass
```

---

## 🚀 Performance Tips

### 1. Async All The Things

```python
# ✅ Non-blocking
async def process_multiple_images(images: List[str]):
    tasks = [process_image(img) for img in images]
    results = await asyncio.gather(*tasks)
    return results

# ❌ Blocking
def process_multiple_images(images: List[str]):
    results = []
    for img in images:
        result = process_image(img)  # Waits for each
        results.append(result)
    return results
```

### 2. Cache Aggressively

```python
from functools import lru_cache

# Cache model loading
@lru_cache(maxsize=1)
def load_model(model_name: str):
    return expensive_model_loading(model_name)

# Cache API results
def get_result(task_id: str):
    if task_id in cache:
        return cache[task_id]
    result = compute_result()
    cache[task_id] = result
    return result
```

### 3. Optimize Image Sizes

```python
def optimize_image(image_path: str, max_size: int = 1024):
    img = Image.open(image_path)
    
    # Resize if too large
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img = img.resize(new_size, Image.LANCZOS)
    
    return img
```

### 4. Batch When Possible

```python
# ✅ Process in batches
def process_batch(images: List[str], batch_size: int = 4):
    for i in range(0, len(images), batch_size):
        batch = images[i:i + batch_size]
        results = model.process(batch)
        yield results

# ❌ Process one by one
def process_one_by_one(images: List[str]):
    for img in images:
        result = model.process(img)  # Inefficient
        yield result
```

---

## 💰 Cost Optimization Tips

### 1. Monitor API Usage

```python
# Track API costs
class APIUsageTracker:
    def __init__(self):
        self.costs = defaultdict(float)
    
    def track(self, service: str, cost: float):
        self.costs[service] += cost
        logger.info(f"Total {service} cost: ${self.costs[service]:.2f}")
```

### 2. Use Cheaper Models When Possible

```python
def choose_model(task_complexity: str):
    if task_complexity == "simple":
        return "gpt-3.5-turbo"  # Cheaper
    elif task_complexity == "medium":
        return "gpt-4"
    else:
        return "gpt-4-turbo"  # Most expensive but best
```

### 3. Cache External API Results

```python
@lru_cache(maxsize=1000)
def get_api_result(prompt: str):
    # Expensive API call
    return api.call(prompt)
```

### 4. Use Spot Instances for GPU

```bash
# AWS Spot instances can save 70-90%
# But can be interrupted, so:
# - Save progress frequently
# - Have fallback to on-demand
# - Use for batch/non-critical tasks
```

---

## 🔒 Security Tips

### 1. Never Commit Secrets

```bash
# .gitignore
.env
.env.*
*.key
secrets.json
config.prod.yml
```

### 2. Validate All Inputs

```python
def validate_image_upload(file: UploadFile):
    # Check file type
    if not file.content_type.startswith("image/"):
        raise ValueError("Must be an image")
    
    # Check file size
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise ValueError("File too large")
    
    # Check content (not just extension)
    try:
        img = Image.open(file.file)
        img.verify()
    except:
        raise ValueError("Invalid image file")
```

### 3. Sanitize Filenames

```python
def sanitize_filename(filename: str) -> str:
    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")
    
    # Remove dangerous characters
    filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
    
    # Limit length
    return filename[:255]
```

### 4. Rate Limit API

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/enhance")
@limiter.limit("10/minute")  # 10 requests per minute
async def enhance_image():
    pass
```

---

## 🐛 Debugging Tips

### 1. Use Structured Logging

```python
logger.info(
    "Task processed",
    extra={
        "task_id": task_id,
        "task_type": task_type,
        "duration_ms": duration,
        "status": status
    }
)
```

### 2. Add Debug Endpoints

```python
@app.get("/debug/state/{task_id}")
async def get_debug_state(task_id: str):
    if not settings.DEBUG:
        raise HTTPException(403, "Debug mode disabled")
    return tasks_db.get(task_id)
```

### 3. Use Breakpoints

```python
# Add breakpoint for debugging
import pdb; pdb.set_trace()

# Or use IDE breakpoints (VS Code, PyCharm)
```

### 4. Test with Small Data First

```python
# ✅ Start small
test_image = create_small_test_image(size=(256, 256))
result = process(test_image)

# ❌ Don't start with
huge_image = load_image("4K_photo.jpg")  # Will take forever
```

---

## 📊 Monitoring Tips

### 1. Track Key Metrics

```python
metrics = {
    "total_requests": 0,
    "success_rate": 0.0,
    "avg_processing_time": 0.0,
    "error_count": 0,
    "api_costs": 0.0
}
```

### 2. Set Up Alerts

```python
def check_error_rate():
    error_rate = errors / total_requests
    if error_rate > 0.05:  # More than 5% errors
        send_alert("High error rate!")
```

### 3. Health Checks

```python
@app.get("/health")
async def health_check():
    checks = {
        "api": check_api_connection(),
        "db": check_db_connection(),
        "disk": check_disk_space(),
        "memory": check_memory_usage()
    }
    
    if all(checks.values()):
        return {"status": "healthy", "checks": checks}
    return {"status": "unhealthy", "checks": checks}
```

---

## 🎨 Code Quality Tips

### 1. Use Linters

```bash
# Install
pip install black flake8 mypy

# Format code
black backend/

# Check style
flake8 backend/

# Type check
mypy backend/
```

### 2. Write Docstrings

```python
def process_image(image_path: str, task_type: str) -> str:
    """
    Process image based on task type.
    
    Args:
        image_path: Path to input image
        task_type: Type of processing (deblur, inpaint, etc.)
    
    Returns:
        Path to processed image
    
    Raises:
        ValueError: If task_type is invalid
        FileNotFoundError: If image_path doesn't exist
    """
    pass
```

### 3. Keep Functions Small

```python
# ✅ Small, focused functions
def validate_input(data):
    pass

def process_data(data):
    pass

def save_result(result):
    pass

# ❌ God function
def do_everything(data):
    # 500 lines of code
    pass
```

---

## 🌐 Deployment Tips

### 1. Use Environment Variables

```python
# ✅ Good
API_KEY = os.getenv("OPENAI_API_KEY")

# ❌ Bad
API_KEY = "sk-1234567890"  # Hardcoded
```

### 2. Health Checks in Docker

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:8000/health || exit 1
```

### 3. Graceful Shutdown

```python
import signal

def graceful_shutdown(signum, frame):
    logger.info("Shutting down gracefully...")
    # Close connections
    # Save state
    # Cleanup
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
```

### 4. Rolling Updates

```bash
# Use rolling updates to avoid downtime
docker-compose up -d --no-deps --build backend
```

---

## 🎓 Learning Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/
- **Streamlit**: https://docs.streamlit.io/

### Courses
- FastAPI course on Udemy
- LangChain tutorials on YouTube
- Computer Vision courses on Coursera

### Communities
- FastAPI Discord
- LangChain Discord
- r/computervision Reddit
- HuggingFace Forums

---

## 📝 Final Tips

1. **Start Simple**: Don't over-engineer từ đầu
2. **Iterate Fast**: Release early, get feedback
3. **Document Everything**: Future you will thank you
4. **Test Often**: Catch bugs early
5. **Monitor Always**: Know what's happening
6. **Optimize Later**: Make it work first, then make it fast
7. **Ask for Help**: Community is friendly
8. **Have Fun**: Enjoy the process! 🎉

---

## ⚠️ Common Pitfalls to Avoid

1. ❌ **Loading all models at startup** → Load on-demand
2. ❌ **Not handling API rate limits** → Implement backoff
3. ❌ **Ignoring memory leaks** → Monitor and cleanup
4. ❌ **Not validating inputs** → Security issues
5. ❌ **Hardcoding values** → Use config files
6. ❌ **No error handling** → App crashes
7. ❌ **Not logging** → Can't debug issues
8. ❌ **Premature optimization** → Wasted time

---

**Remember**: Perfect is the enemy of done. Ship it! 🚀
