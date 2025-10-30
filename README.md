# Deep Vision 🎨

Một ứng dụng web chỉnh sửa ảnh thông minh sử dụng Deep Learning với kiến trúc client-server.

## Tính năng

✨ **Các hiệu ứng chỉnh sửa ảnh:**
- Grayscale (Đen trắng)
- Blur (Làm mờ) với điều chỉnh độ mạnh
- Sharpen (Làm sắc nét)
- Edge Detection (Phát hiện cạnh)
- Sepia Tone (Tông màu nâu cổ điển)
- Brightness (Độ sáng) với điều chỉnh
- Contrast (Độ tương phản) với điều chỉnh
- Invert Colors (Đảo màu)
- Cartoon Effect (Hiệu ứng hoạt hình)
- Emboss (Nổi bật)

🚀 **Tính năng khác:**
- Giao diện web hiện đại, thân thiện
- Upload ảnh qua kéo thả (drag & drop)
- Xem trước ảnh gốc và ảnh đã chỉnh sửa
- Tải xuống ảnh đã xử lý
- API RESTful cho backend
- Hỗ trợ nhiều định dạng ảnh (PNG, JPG, JPEG, GIF, BMP)

## Yêu cầu hệ thống

- Python 3.8+
- pip (Python package manager)

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/minhduonq/deep_vision.git
cd deep_vision
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

**Lưu ý:** Nếu bạn muốn sử dụng PyTorch với GPU (CUDA), hãy cài đặt phiên bản tương ứng từ [pytorch.org](https://pytorch.org/).

## Sử dụng

### Khởi động server

```bash
python server.py
```

Server sẽ chạy tại: `http://localhost:5000`

### Truy cập ứng dụng

Mở trình duyệt web và truy cập:
```
http://localhost:5000
```

### Sử dụng ứng dụng

1. **Tải ảnh lên:**
   - Nhấn nút "Chọn Ảnh" hoặc kéo thả ảnh vào vùng upload
   
2. **Chọn hiệu ứng:**
   - Chọn một trong các hiệu ứng có sẵn
   - Điều chỉnh tham số nếu có (ví dụ: độ mạnh blur, độ sáng)
   
3. **Áp dụng:**
   - Nhấn nút "Áp Dụng Hiệu Ứng"
   - Xem kết quả ở cột "Ảnh Đã Chỉnh Sửa"
   
4. **Tải xuống:**
   - Nhấn nút "Tải Xuống" để lưu ảnh đã chỉnh sửa

## Kiến trúc hệ thống

### Backend (Flask Server)
- **Framework:** Flask
- **Deep Learning:** OpenCV, PyTorch
- **API Endpoints:**
  - `GET /` - Trang chủ
  - `POST /api/upload` - Upload ảnh
  - `POST /api/process` - Xử lý ảnh với hiệu ứng
  - `GET /api/download/<filename>` - Tải xuống ảnh
  - `GET /api/operations` - Danh sách hiệu ứng

### Frontend (HTML/CSS/JavaScript)
- Giao diện responsive
- Drag & drop upload
- Real-time preview
- AJAX calls để giao tiếp với backend

### Xử lý ảnh
- **OpenCV:** Các bộ lọc và hiệu ứng cơ bản
- **PyTorch:** Sẵn sàng cho các mô hình deep learning nâng cao
- **Pillow:** Xử lý và lưu ảnh

## Cấu trúc thư mục

```
deep_vision/
├── server.py           # Backend Flask server
├── requirements.txt    # Python dependencies
├── README.md          # Documentation
├── static/            # Frontend files
│   └── index.html     # Main web interface
└── uploads/           # Uploaded and processed images (auto-created)
```

## API Documentation

### Upload Image
```http
POST /api/upload
Content-Type: multipart/form-data

file: <image_file>
```

Response:
```json
{
  "success": true,
  "filename": "image.jpg",
  "message": "File uploaded successfully"
}
```

### Process Image
```http
POST /api/process
Content-Type: application/json

{
  "filename": "image.jpg",
  "operation": "blur",
  "params": {
    "strength": 5
  }
}
```

Response:
```json
{
  "success": true,
  "filename": "processed_image.jpg",
  "message": "Image processed successfully"
}
```

### Get Available Operations
```http
GET /api/operations
```

Response:
```json
[
  {
    "name": "blur",
    "label": "Blur",
    "params": [
      {
        "name": "strength",
        "type": "number",
        "default": 5,
        "min": 1,
        "max": 20
      }
    ]
  }
]
```

## Mở rộng

### Thêm hiệu ứng mới

1. Thêm hàm xử lý trong `server.py`:
```python
def apply_my_filter(image, param1=1.0):
    """Your filter implementation"""
    img_array = np.array(image)
    # Process image
    return processed_array
```

2. Thêm vào endpoint `/api/process`:
```python
elif operation == 'my_filter':
    result = apply_my_filter(image, params.get('param1', 1.0))
    result = Image.fromarray(result)
```

3. Thêm vào danh sách operations trong `/api/operations`:
```python
{'name': 'my_filter', 'label': 'My Filter', 'params': [...]}
```

## Giấy phép

MIT License

## Tác giả

Minh Duong

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo pull request hoặc mở issue để thảo luận.
