import torch

print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Device count: {torch.cuda.device_count()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA: Not available")
    print("Possible reasons:")
    print("1. No NVIDIA GPU")
    print("2. CUDA drivers not installed")
    print("3. PyTorch CPU-only version installed")
