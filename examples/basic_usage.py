"""Example usage of Deep Vision library."""

from PIL import Image
from deep_vision import ImageEditor


def example_basic_edit():
    """Basic example of editing an image with a prompt."""
    # Initialize the editor
    editor = ImageEditor(device="cuda")  # or "cpu" if no GPU
    
    # Edit an image with a simple prompt
    result = editor.edit_image(
        image="input.jpg",
        prompt="make the sky more blue and vibrant",
        guidance_scale=7.5,
        num_inference_steps=50,
    )
    
    # Save the result
    result.save("output_basic.jpg")
    print("Saved basic edit to output_basic.jpg")


def example_remove_object():
    """Example of removing an object from an image."""
    editor = ImageEditor()
    
    # Remove an object
    result = editor.remove_object(
        image="photo_with_person.jpg",
        object_description="the person in the background",
    )
    
    result.save("output_removed.jpg")
    print("Saved object removal to output_removed.jpg")


def example_sharpen():
    """Example of sharpening an image."""
    editor = ImageEditor()
    
    # Sharpen the image
    result = editor.sharpen_image(
        image="blurry_photo.jpg",
        intensity="high",
    )
    
    result.save("output_sharp.jpg")
    print("Saved sharpened image to output_sharp.jpg")


def example_add_object():
    """Example of adding an object to an image."""
    editor = ImageEditor()
    
    # Add an object
    result = editor.add_object(
        image="landscape.jpg",
        object_description="a red balloon",
        location="in the center of the sky",
    )
    
    result.save("output_added.jpg")
    print("Saved image with added object to output_added.jpg")


def example_beautify():
    """Example of beautifying a portrait."""
    editor = ImageEditor()
    
    # Beautify the image
    result = editor.beautify(
        image="portrait.jpg",
        features=["skin", "eyes"],
    )
    
    result.save("output_beauty.jpg")
    print("Saved beautified image to output_beauty.jpg")


def example_custom_prompt():
    """Example with a custom creative prompt."""
    editor = ImageEditor()
    
    # Use a creative prompt
    result = editor.edit_image(
        image="landscape.jpg",
        prompt="transform into a beautiful sunset scene with warm orange and pink colors",
        negative_prompt="dark, gloomy, overcast",
        guidance_scale=8.0,
        num_inference_steps=75,
        seed=42,  # for reproducibility
    )
    
    result.save("output_sunset.jpg")
    print("Saved custom edit to output_sunset.jpg")


def example_batch_processing():
    """Example of processing multiple images."""
    import os
    
    editor = ImageEditor()
    
    input_dir = "input_images"
    output_dir = "output_images"
    os.makedirs(output_dir, exist_ok=True)
    
    prompts = {
        "photo1.jpg": "enhance colors and make more vibrant",
        "photo2.jpg": "remove the watermark",
        "photo3.jpg": "make the image brighter and clearer",
    }
    
    for filename, prompt in prompts.items():
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"edited_{filename}")
        
        if os.path.exists(input_path):
            result = editor.edit_image(
                image=input_path,
                prompt=prompt,
            )
            result.save(output_path)
            print(f"Processed {filename} -> edited_{filename}")


if __name__ == "__main__":
    print("Deep Vision Examples")
    print("====================")
    print()
    print("Uncomment the example you want to run:")
    print()
    
    # Uncomment one of these to run:
    # example_basic_edit()
    # example_remove_object()
    # example_sharpen()
    # example_add_object()
    # example_beautify()
    # example_custom_prompt()
    # example_batch_processing()
    
    print("Please uncomment an example function in the code to run it.")
