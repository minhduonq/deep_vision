# Quick Start Guide

This guide will help you get started with Deep Vision in just a few minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/minhduonq/deep_vision.git
cd deep_vision

# Install dependencies
pip install -r requirements.txt
```

## Your First Edit

Here's a simple example to edit an image:

```python
from deep_vision import ImageEditor
from PIL import Image

# Create a sample image or use your own
# For this example, let's use an existing image
editor = ImageEditor(device="cpu")  # Use "cuda" if you have GPU

# Edit the image
result = editor.edit_image(
    image="your_image.jpg",
    prompt="make the image brighter and more colorful"
)

# Save the result
result.save("edited_image.jpg")
print("Done! Check edited_image.jpg")
```

## Common Use Cases

### 1. Remove Something from an Image

```python
from deep_vision import ImageEditor

editor = ImageEditor()

# Remove a person from the background
result = editor.remove_object(
    image="photo.jpg",
    object_description="person in the background"
)
result.save("cleaned_photo.jpg")
```

### 2. Make an Image Sharper

```python
# Sharpen a blurry image
result = editor.sharpen_image(
    image="blurry.jpg",
    intensity="high"
)
result.save("sharp.jpg")
```

### 3. Add Something to an Image

```python
# Add an object to the scene
result = editor.add_object(
    image="landscape.jpg",
    object_description="a rainbow",
    location="in the sky"
)
result.save("landscape_with_rainbow.jpg")
```

### 4. Beauty Enhancement

```python
# Enhance a portrait
result = editor.beautify(
    image="portrait.jpg",
    features=["skin", "eyes"]
)
result.save("beautiful_portrait.jpg")
```

## Using the Command Line

You can also use Deep Vision from the command line:

```bash
# Basic edit
python -m deep_vision.cli input.jpg "make it brighter" -o output.jpg

# Remove object
python -m deep_vision.cli photo.jpg "person" --mode remove -o cleaned.jpg

# Sharpen
python -m deep_vision.cli blurry.jpg "high" --mode sharpen -o sharp.jpg
```

## Parameters Explained

- **prompt**: What you want to do (e.g., "make the sky blue", "remove the person")
- **negative_prompt**: What you want to avoid (e.g., "dark, blurry, low quality")
- **guidance_scale**: How closely to follow your prompt (7.5 is default, higher = more strict)
- **num_inference_steps**: Quality vs speed (50 is default, higher = better quality but slower)
- **seed**: For reproducible results (use same seed for same output)

## Tips for Better Results

1. **Be specific in your prompts**
   - Good: "make the sky bright blue with white clouds"
   - Bad: "change sky"

2. **Use negative prompts**
   ```python
   result = editor.edit_image(
       image="photo.jpg",
       prompt="beautiful sunset",
       negative_prompt="dark, gloomy, cloudy"
   )
   ```

3. **Adjust guidance_scale for control**
   - Lower (5-7): More creative, less strict
   - Higher (8-12): More strict to prompt

4. **Use GPU for speed**
   ```python
   editor = ImageEditor(device="cuda")  # Much faster!
   ```

## Next Steps

- Check out `examples/basic_usage.py` for more examples
- Read the full documentation in README.md
- For Vietnamese documentation, see VIETNAMESE.md

## Troubleshooting

**Out of memory?**
```python
# Use CPU instead of GPU
editor = ImageEditor(device="cpu")
```

**Results not good?**
- Try different guidance_scale values
- Increase num_inference_steps
- Make your prompt more specific
- Add a negative prompt

**Too slow?**
- Use GPU if available
- Reduce num_inference_steps to 30
- Resize your input image to be smaller

Need help? Open an issue on GitHub!
