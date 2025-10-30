# Deep Vision

A powerful image editing library using deep learning models that allows you to edit images based on natural language prompts.

## Features

- **Prompt-based editing**: Edit images using simple text descriptions
- **Object removal**: Remove unwanted objects from images
- **Image sharpening**: Enhance image details and clarity
- **Object addition**: Add new objects to images naturally
- **Beauty enhancement**: Apply beauty filters and enhancements
- **Custom edits**: Any creative transformation you can describe

## Installation

```bash
pip install -r requirements.txt
```

Or install from source:

```bash
git clone https://github.com/minhduonq/deep_vision.git
cd deep_vision
pip install -e .
```

## Requirements

- Python >= 3.8
- PyTorch >= 2.0.0
- CUDA (optional, for GPU acceleration)

## Quick Start

### Using the Python API

```python
from deep_vision import ImageEditor

# Initialize the editor
editor = ImageEditor(device="cuda")  # or "cpu"

# Edit an image with a prompt
result = editor.edit_image(
    image="input.jpg",
    prompt="make the sky more blue and vibrant",
    guidance_scale=7.5,
    num_inference_steps=50,
)
result.save("output.jpg")
```

### Using the Command Line

```bash
python -m deep_vision.cli input.jpg "make the sky blue" -o output.jpg
```

## Usage Examples

### Remove an Object

```python
from deep_vision import ImageEditor

editor = ImageEditor()
result = editor.remove_object(
    image="photo.jpg",
    object_description="the person in the background"
)
result.save("output.jpg")
```

### Sharpen an Image

```python
result = editor.sharpen_image(
    image="blurry.jpg",
    intensity="high"
)
result.save("sharp.jpg")
```

### Add an Object

```python
result = editor.add_object(
    image="landscape.jpg",
    object_description="a red balloon",
    location="in the center of the sky"
)
result.save("with_balloon.jpg")
```

### Beautify a Portrait

```python
result = editor.beautify(
    image="portrait.jpg",
    features=["skin", "eyes"]
)
result.save("beautiful.jpg")
```

### Custom Prompt

```python
result = editor.edit_image(
    image="photo.jpg",
    prompt="transform into a beautiful sunset scene",
    negative_prompt="dark, gloomy",
    guidance_scale=8.0,
    seed=42
)
result.save("sunset.jpg")
```

## Command Line Interface

The CLI provides easy access to all features:

```bash
# Basic editing
python -m deep_vision.cli input.jpg "your prompt" -o output.jpg

# Remove object
python -m deep_vision.cli input.jpg "the person" --mode remove -o output.jpg

# Sharpen image
python -m deep_vision.cli input.jpg "high" --mode sharpen -o output.jpg

# Add object
python -m deep_vision.cli input.jpg "a tree" --mode add -o output.jpg

# Beautify
python -m deep_vision.cli portrait.jpg "" --mode beautify -o output.jpg

# With additional parameters
python -m deep_vision.cli input.jpg "make it vibrant" \
    --guidance-scale 8.0 \
    --steps 75 \
    --seed 42 \
    --negative-prompt "dark, low quality" \
    -o output.jpg
```

## Parameters

- `prompt`: Text description of the desired edit
- `negative_prompt`: Things to avoid in the output (optional)
- `strength`: How much to transform (0.0-1.0, default: 0.75)
- `guidance_scale`: How closely to follow the prompt (default: 7.5)
- `num_inference_steps`: Quality vs speed tradeoff (default: 50)
- `seed`: Random seed for reproducibility (optional)

## How It Works

Deep Vision uses state-of-the-art diffusion models:

- **InstructPix2Pix**: For general image editing based on instructions
- **Stable Diffusion Inpainting**: For object removal and inpainting tasks

The system automatically analyzes your prompt to determine the best approach for your editing task.

## Examples

See the `examples/` directory for more detailed usage examples:

- `basic_usage.py`: Comprehensive examples of all features
- More examples coming soon!

## Performance Tips

1. **Use GPU**: Enable CUDA for much faster processing
2. **Reduce steps**: Lower `num_inference_steps` for faster results
3. **Resize images**: Large images are automatically resized to 512px
4. **Batch processing**: Process multiple images efficiently

## Supported Languages

Prompts work best in English, but the system can understand:
- Vietnamese (Tiếng Việt)
- English
- Other languages (with varying quality)

## Vietnamese Usage / Sử dụng tiếng Việt

```python
from deep_vision import ImageEditor

editor = ImageEditor()

# Xóa vật thể
result = editor.remove_object(
    image="anh.jpg",
    object_description="người ở phía sau"
)

# Làm nét ảnh
result = editor.sharpen_image(
    image="anh_mo.jpg",
    intensity="high"
)

# Thêm vật thể
result = editor.add_object(
    image="phong_canh.jpg",
    object_description="bong bay màu đỏ",
    location="ở giữa bầu trời"
)

# Làm đẹp
result = editor.beautify(
    image="chan_dung.jpg",
    features=["da", "mắt"]
)
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

This project uses:
- [Stable Diffusion](https://github.com/CompVis/stable-diffusion)
- [InstructPix2Pix](https://github.com/timothybrooks/instruct-pix2pix)
- [Hugging Face Diffusers](https://github.com/huggingface/diffusers)
