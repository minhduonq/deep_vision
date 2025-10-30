# Hướng Dẫn Sử Dụng Deep Vision (Vietnamese)

Deep Vision là thư viện chỉnh sửa ảnh mạnh mẽ sử dụng deep learning, cho phép bạn chỉnh sửa ảnh dựa trên mô tả bằng ngôn ngữ tự nhiên.

## Cài Đặt

```bash
pip install -r requirements.txt
```

Hoặc cài đặt từ mã nguồn:

```bash
git clone https://github.com/minhduonq/deep_vision.git
cd deep_vision
pip install -e .
```

## Yêu Cầu Hệ Thống

- Python >= 3.8
- PyTorch >= 2.0.0
- CUDA (tùy chọn, để tăng tốc với GPU)

## Bắt Đầu Nhanh

### Sử dụng Python API

```python
from deep_vision import ImageEditor

# Khởi tạo trình chỉnh sửa
editor = ImageEditor(device="cuda")  # hoặc "cpu"

# Chỉnh sửa ảnh với prompt
result = editor.edit_image(
    image="anh_dau_vao.jpg",
    prompt="làm bầu trời xanh hơn và rực rỡ hơn",
    guidance_scale=7.5,
    num_inference_steps=50,
)
result.save("anh_dau_ra.jpg")
```

### Sử dụng Dòng Lệnh

```bash
python -m deep_vision.cli anh_dau_vao.jpg "làm bầu trời xanh hơn" -o anh_dau_ra.jpg
```

## Các Ví Dụ Sử Dụng

### 1. Xóa Vật Thể

```python
from deep_vision import ImageEditor

editor = ImageEditor()
result = editor.remove_object(
    image="anh.jpg",
    object_description="người ở phía sau"
)
result.save("anh_da_xoa.jpg")
```

**Dòng lệnh:**
```bash
python -m deep_vision.cli anh.jpg "người ở phía sau" --mode remove -o anh_da_xoa.jpg
```

### 2. Làm Nét Ảnh

```python
result = editor.sharpen_image(
    image="anh_mo.jpg",
    intensity="high"  # có thể là "low", "medium", hoặc "high"
)
result.save("anh_net.jpg")
```

**Dòng lệnh:**
```bash
python -m deep_vision.cli anh_mo.jpg "high" --mode sharpen -o anh_net.jpg
```

### 3. Thêm Vật Thể

```python
result = editor.add_object(
    image="phong_canh.jpg",
    object_description="bong bay màu đỏ",
    location="ở giữa bầu trời"
)
result.save("anh_them_vat_the.jpg")
```

**Dòng lệnh:**
```bash
python -m deep_vision.cli phong_canh.jpg "bong bay màu đỏ" --mode add -o anh_them_vat_the.jpg
```

### 4. Làm Đẹp

```python
result = editor.beautify(
    image="chan_dung.jpg",
    features=["da", "mắt", "răng"]
)
result.save("anh_dep.jpg")
```

**Dòng lệnh:**
```bash
python -m deep_vision.cli chan_dung.jpg "" --mode beautify -o anh_dep.jpg
```

### 5. Chỉnh Sửa Tùy Chỉnh

```python
result = editor.edit_image(
    image="anh.jpg",
    prompt="biến thành cảnh hoàng hôn đẹp với màu cam và hồng ấm áp",
    negative_prompt="tối, u ám, nhiều mây",
    guidance_scale=8.0,
    num_inference_steps=75,
    seed=42,  # để có kết quả lặp lại được
)
result.save("anh_hoang_hon.jpg")
```

## Các Tham Số

- `prompt`: Mô tả văn bản về chỉnh sửa mong muốn
- `negative_prompt`: Những gì cần tránh trong kết quả (tùy chọn)
- `strength`: Mức độ biến đổi (0.0-1.0, mặc định: 0.75)
- `guidance_scale`: Mức độ tuân theo prompt (mặc định: 7.5)
- `num_inference_steps`: Đánh đổi giữa chất lượng và tốc độ (mặc định: 50)
- `seed`: Seed ngẫu nhiên để có kết quả lặp lại (tùy chọn)

## Các Loại Chỉnh Sửa Được Hỗ Trợ

### Xóa Vật Thể
- Xóa người, vật thể không mong muốn
- Làm sạch background
- Xóa watermark

**Ví dụ prompt:**
- "xóa người trong ảnh"
- "xóa chữ ở góc dưới"
- "xóa đồ vật trên bàn"

### Làm Nét Ảnh
- Tăng độ nét
- Tăng chi tiết
- Làm rõ ảnh mờ

**Ví dụ prompt:**
- "làm nét ảnh"
- "tăng chi tiết"
- "làm rõ hơn"

### Thêm Vật Thể
- Thêm người, vật thể mới
- Chèn đồ vật vào cảnh
- Tạo thêm chi tiết

**Ví dụ prompt:**
- "thêm cây xanh ở bên trái"
- "thêm chim bay trên trời"
- "đặt hoa ở trên bàn"

### Làm Đẹp
- Làm mịn da
- Tăng độ sáng mắt
- Làm trắng răng
- Chỉnh màu da

**Ví dụ prompt:**
- "làm đẹp khuôn mặt"
- "làm mịn da"
- "tăng độ sáng mắt"

### Chỉnh Sửa Chung
- Thay đổi màu sắc
- Điều chỉnh ánh sáng
- Thay đổi phong cách
- Và nhiều hơn nữa

**Ví dụ prompt:**
- "làm ảnh sáng hơn"
- "thêm màu ấm"
- "biến thành phong cách anime"
- "làm nền mờ đi"

## Xử Lý Hàng Loạt

```python
import os
from deep_vision import ImageEditor

editor = ImageEditor()

# Danh sách ảnh và prompt
images_prompts = {
    "anh1.jpg": "làm sáng hơn",
    "anh2.jpg": "xóa người ở phía sau",
    "anh3.jpg": "làm nét ảnh",
}

# Xử lý từng ảnh
for image_file, prompt in images_prompts.items():
    result = editor.edit_image(
        image=image_file,
        prompt=prompt,
    )
    output_name = f"edited_{image_file}"
    result.save(output_name)
    print(f"Đã xử lý {image_file} -> {output_name}")
```

## Lời Khuyên Hiệu Suất

1. **Sử dụng GPU**: Bật CUDA để xử lý nhanh hơn nhiều
   ```python
   editor = ImageEditor(device="cuda")
   ```

2. **Giảm số bước**: Giảm `num_inference_steps` để có kết quả nhanh hơn
   ```python
   result = editor.edit_image(image="anh.jpg", prompt="...", num_inference_steps=30)
   ```

3. **Kích thước ảnh**: Ảnh lớn sẽ tự động được resize về 512px để xử lý nhanh hơn

4. **Xử lý hàng loạt**: Khởi tạo editor một lần và dùng lại cho nhiều ảnh

## Ví Dụ Thực Tế

### Chỉnh Sửa Ảnh Chân Dung
```python
editor = ImageEditor(device="cuda")

# Làm đẹp
result = editor.beautify(
    image="chan_dung.jpg",
    features=["da", "mắt"]
)
result.save("chan_dung_dep.jpg")

# Xóa background
result = editor.edit_image(
    image="chan_dung.jpg",
    prompt="nền trắng sạch, chỉ giữ người",
)
result.save("chan_dung_nen_trang.jpg")
```

### Chỉnh Sửa Ảnh Phong Cảnh
```python
# Thay đổi thời tiết
result = editor.edit_image(
    image="phong_canh.jpg",
    prompt="trời xanh, mây trắng, nắng đẹp",
    negative_prompt="mưa, tối, u ám"
)
result.save("phong_canh_nang_dep.jpg")

# Thêm chi tiết
result = editor.add_object(
    image="phong_canh.jpg",
    object_description="đàn chim bay",
    location="trên bầu trời"
)
result.save("phong_canh_co_chim.jpg")
```

### Chỉnh Sửa Ảnh Sản Phẩm
```python
# Xóa background
result = editor.remove_object(
    image="san_pham.jpg",
    object_description="nền lộn xộn"
)
result.save("san_pham_nen_sach.jpg")

# Làm nét chi tiết
result = editor.sharpen_image(
    image="san_pham.jpg",
    intensity="high"
)
result.save("san_pham_net.jpg")
```

## Khắc Phục Sự Cố

### Lỗi thiếu bộ nhớ GPU
```python
# Sử dụng CPU thay vì
editor = ImageEditor(device="cpu")
```

### Kết quả không như mong đợi
- Thử điều chỉnh `guidance_scale` (7.5-10.0)
- Tăng `num_inference_steps` (50-100)
- Thêm `negative_prompt` rõ ràng hơn
- Thử các seed khác nhau

### Tốc độ xử lý chậm
- Sử dụng GPU nếu có
- Giảm `num_inference_steps`
- Giảm kích thước ảnh đầu vào

## Giấy Phép

MIT License

## Đóng Góp

Mọi đóng góp đều được chào đón! Vui lòng gửi Pull Request.

## Liên Hệ

- GitHub Issues: [https://github.com/minhduonq/deep_vision/issues](https://github.com/minhduonq/deep_vision/issues)
