## Sample <code>.env</code> file structure
```
# LLM API Keys (for agent coordination)
OPENAI_API_KEY="YOUR OPEN AI KEY"
ANTHROPIC_API_KEY="YOUR KEY"

# Image Model APIs
REPLICATE_API_TOKEN="YOUR_KEY" - NEED TO CALL NANO-BANANA API
HUGGINGFACE_API_TOKEN=YOUR HF TOKEN

# Application Settings
APP_NAME=DeepVision
APP_VERSION=0.1.0
DEBUG=True
LOG_LEVEL=INFO

# Server Settings
HOST=0.0.0.0
PORT=8000
WORKERS=1

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8501,http://localhost:8000

# Storage Paths
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
MODEL_DIR=./models
CACHE_DIR=./cache

# GPU Settings
CUDA_VISIBLE_DEVICES=0
MAX_BATCH_SIZE=1
DEVICE=cuda  # or cpu
ENABLE_XFORMERS=False

# Model Settings
USE_LOCAL_MODELS=False  # Set to True if running models locally
MAX_IMAGE_SIZE=2048
DEFAULT_IMAGE_SIZE=512

# Local Model Selection (when USE_LOCAL_MODELS=True)
DEBLUR_MODEL=nafnet  # nafnet, swinir
INPAINT_MODEL=lama  # lama, mat
BEAUTY_MODEL=gfpgan  # gfpgan, codeformer
GENERATION_MODEL=huggingface  # huggingface, replicate, local_sd

# Processing Settings
MAX_CONCURRENT_TASKS=3
TASK_TIMEOUT=300  # seconds
CLEANUP_INTERVAL=3600  # seconds

# Database (Optional)
# DATABASE_URL=postgresql://user:password@localhost/deepvision

# Redis (Optional - for task queue)
# REDIS_URL=redis://localhost:6379/0

# Monitoring (Optional)
# SENTRY_DSN=
# ENABLE_METRICS=True
# METRICS_PORT=9090

```
