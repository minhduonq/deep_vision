# Ví dụ sử dụng Deep Vision

## 1. Khởi động server

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
python server.py
```

Server sẽ khởi động tại `http://localhost:5000`

## 2. Sử dụng Web Interface

### Bước 1: Mở trình duyệt
Truy cập: `http://localhost:5000`

### Bước 2: Tải ảnh lên
- Nhấn nút "Chọn Ảnh" hoặc kéo thả ảnh vào vùng upload
- Hỗ trợ các định dạng: PNG, JPG, JPEG, GIF, BMP

### Bước 3: Chọn và áp dụng hiệu ứng
- Chọn một trong 10 hiệu ứng có sẵn
- Điều chỉnh tham số nếu cần (ví dụ: độ mạnh blur, độ sáng)
- Nhấn "Áp Dụng Hiệu Ứng"

### Bước 4: Tải xuống
- Nhấn nút "Tải Xuống" để lưu ảnh đã chỉnh sửa

## 3. Sử dụng API (cho Developer)

### Upload ảnh

```python
import requests

url = "http://localhost:5000/api/upload"
files = {'file': open('image.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.json())
# Output: {"success": true, "filename": "image.jpg", ...}
```

### Xử lý ảnh

```python
import requests

url = "http://localhost:5000/api/process"
payload = {
    "filename": "image.jpg",
    "operation": "blur",
    "params": {"strength": 10}
}
response = requests.post(url, json=payload)
print(response.json())
# Output: {"success": true, "filename": "processed_image.jpg", ...}
```

### Tải xuống ảnh

```python
import requests

url = "http://localhost:5000/api/download/processed_image.jpg"
response = requests.get(url)
with open('result.jpg', 'wb') as f:
    f.write(response.content)
```

### Lấy danh sách operations

```python
import requests

url = "http://localhost:5000/api/operations"
response = requests.get(url)
operations = response.json()
for op in operations:
    print(f"{op['label']}: {op['name']}")
```

## 4. Các hiệu ứng có sẵn

| Tên hiệu ứng | Mô tả | Tham số |
|-------------|-------|---------|
| Grayscale | Chuyển ảnh sang đen trắng | Không |
| Blur | Làm mờ ảnh | strength (1-20) |
| Sharpen | Làm sắc nét ảnh | Không |
| Edge Detection | Phát hiện cạnh | Không |
| Sepia Tone | Tông màu nâu cổ điển | Không |
| Brightness | Điều chỉnh độ sáng | factor (0.1-3.0) |
| Contrast | Điều chỉnh độ tương phản | factor (0.1-3.0) |
| Invert Colors | Đảo ngược màu sắc | Không |
| Cartoon Effect | Hiệu ứng hoạt hình | Không |
| Emboss | Hiệu ứng nổi bật | Không |

## 5. Ví dụ tích hợp

### Tích hợp với Python Script

```python
import requests
import os

class DeepVisionClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def upload_image(self, filepath):
        """Upload ảnh lên server"""
        url = f"{self.base_url}/api/upload"
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            return response.json()
    
    def process_image(self, filename, operation, params=None):
        """Xử lý ảnh với hiệu ứng"""
        url = f"{self.base_url}/api/process"
        payload = {
            "filename": filename,
            "operation": operation,
            "params": params or {}
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def download_image(self, filename, save_path):
        """Tải xuống ảnh đã xử lý"""
        url = f"{self.base_url}/api/download/{filename}"
        response = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path

# Sử dụng
client = DeepVisionClient()

# Upload ảnh gốc
result = client.upload_image("my_photo.jpg")
filename = result['filename']

# Xử lý ảnh - mỗi lần xử lý tạo file mới với tên "processed_<filename>"
# Lần 1: Grayscale
result1 = client.process_image(filename, "grayscale")
processed_filename1 = result1['filename']  # "processed_my_photo.jpg"

# Lần 2: Blur - xử lý trên ảnh gốc
result2 = client.process_image(filename, "blur", {"strength": 5})
processed_filename2 = result2['filename']  # "processed_my_photo.jpg" (ghi đè)

# Lần 3: Cartoon - xử lý trên ảnh gốc
result3 = client.process_image(filename, "cartoon")
processed_filename3 = result3['filename']  # "processed_my_photo.jpg" (ghi đè)

# Tải xuống ảnh cuối cùng (cartoon effect)
client.download_image(processed_filename3, "result.jpg")
```

### Tích hợp với cURL

```bash
# Upload ảnh
curl -X POST -F "file=@image.jpg" http://localhost:5000/api/upload

# Xử lý ảnh
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{"filename":"image.jpg","operation":"blur","params":{"strength":5}}'

# Tải xuống
curl http://localhost:5000/api/download/processed_image.jpg -o result.jpg
```

## 6. Testing

Chạy test script để kiểm tra API:

```bash
python test_api.py
```

Output mẫu:
```
==================================================
Deep Vision Server API Tests
==================================================
Server URL: http://localhost:5000
==================================================
Testing /api/operations endpoint...
✓ Found 10 operations
  - Grayscale (grayscale)
  - Blur (blur)
  ...

Testing /api/upload endpoint...
✓ Upload successful: test_image.png

Testing /api/process endpoint...
✓ grayscale: processed_test_image.png
✓ blur: processed_test_image.png
✓ sharpen: processed_test_image.png

Testing /api/download endpoint...
✓ Download successful: 593 bytes

==================================================
Tests completed!
==================================================
```

## 7. Mở rộng và Custom

### Thêm hiệu ứng mới

Để thêm hiệu ứng mới vào hệ thống, xem hướng dẫn trong README.md.

### Tích hợp Deep Learning Models nâng cao

Hệ thống đã sẵn sàng để tích hợp các mô hình PyTorch. Dưới đây là ví dụ về cách thêm Style Transfer:

```python
# Trong server.py, thêm function mới
def apply_style_transfer(image, style='starry_night'):
    """Apply neural style transfer using PyTorch"""
    if not PYTORCH_AVAILABLE:
        raise Exception("PyTorch required for style transfer")
    
    # Load pretrained model
    model = torch.hub.load('pytorch/vision:v0.10.0', 'vgg19', pretrained=True)
    
    # Preprocessing
    transform = transforms.Compose([
        transforms.Resize(512),
        transforms.ToTensor(),
    ])
    
    # Apply style transfer (simplified example)
    img_tensor = transform(image).unsqueeze(0)
    # ... style transfer logic ...
    
    return result_image
```

Các mô hình có thể thêm:
- **Style Transfer** - Chuyển đổi phong cách nghệ thuật (Van Gogh, Picasso, etc.)
- **Super Resolution** - Tăng độ phân giải ảnh sử dụng ESRGAN
- **Object Detection** - Phát hiện đối tượng với YOLO hoặc Faster R-CNN
- **Face Enhancement** - Cải thiện khuôn mặt với GFPGAN
- **Image Segmentation** - Phân đoạn ảnh với U-Net hoặc DeepLab
- **Colorization** - Tô màu ảnh đen trắng tự động

Tham khảo:
- PyTorch Hub: https://pytorch.org/hub/
- Hugging Face Models: https://huggingface.co/models

## 8. Troubleshooting

### Lỗi: Port 5000 đã được sử dụng
```bash
# Thay đổi port trong server.py
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Lỗi: ModuleNotFoundError
```bash
# Cài đặt lại dependencies
pip install -r requirements.txt
```

### Lỗi: File upload quá lớn
```python
# Tăng MAX_CONTENT_LENGTH trong server.py
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```
