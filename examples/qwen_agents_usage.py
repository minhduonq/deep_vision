"""
Example: Sử dụng Qwen Edit Agents

Hướng dẫn sử dụng các agent mới:
1. QwenFastEditAgent - Single image editing nhanh
2. QwenLoRAFusionAgent - Multi-image fusion với LoRA styles
"""
import asyncio
from pathlib import Path
from backend.agents import (
    qwen_fast_edit_agent,
    qwen_lora_fusion_agent
)


async def example_fast_edit():
    """Example: Fast single image editing"""
    print("\n=== EXAMPLE 1: Fast Single Image Edit ===")
    
    # Đổi màu một object
    result = await qwen_fast_edit_agent.quick_color_change(
        image_path="uploads/test_image.jpg",
        target_object="the car",
        new_color="red"
    )
    
    if result["success"]:
        print(f"✅ Output: {result['output_path']}")
        print(f"   Seed: {result['seed']}")
    else:
        print(f"❌ Error: {result['error']}")


async def example_style_transfer():
    """Example: Style transfer"""
    print("\n=== EXAMPLE 2: Style Transfer ===")
    
    result = await qwen_fast_edit_agent.style_transfer(
        image_path="uploads/photo.jpg",
        style="oil painting"
    )
    
    if result["success"]:
        print(f"✅ Output: {result['output_path']}")


async def example_object_replacement():
    """Example: Replace object between 2 images"""
    print("\n=== EXAMPLE 3: Object Replacement (LoRA Fusion) ===")
    
    result = await qwen_lora_fusion_agent.replace_object(
        source_image="uploads/glasses_reference.jpg",
        target_image="uploads/person.jpg",
        object_name="glasses",
        lora_style="Super-Fusion"
    )
    
    if result["success"]:
        print(f"✅ Output: {result['output_path']}")
        print(f"   LoRA: {result['lora_adapter']}")


async def example_fashion_transfer():
    """Example: Fashion transfer"""
    print("\n=== EXAMPLE 4: Fashion Transfer ===")
    
    result = await qwen_lora_fusion_agent.fashion_transfer(
        clothing_reference="uploads/dress_reference.jpg",
        person_image="uploads/model.jpg"
    )
    
    if result["success"]:
        print(f"✅ Output: {result['output_path']}")


async def example_cinematic_edit():
    """Example: Cinematic editing"""
    print("\n=== EXAMPLE 5: Cinematic Edit ===")
    
    result = await qwen_lora_fusion_agent.cinematic_edit(
        reference_scene="uploads/movie_scene.jpg",
        target_image="uploads/photo.jpg"
    )
    
    if result["success"]:
        print(f"✅ Output: {result['output_path']}")


async def example_batch_edit():
    """Example: Batch editing multiple images"""
    print("\n=== EXAMPLE 6: Batch Edit ===")
    
    images = [
        "uploads/image1.jpg",
        "uploads/image2.jpg",
        "uploads/image3.jpg"
    ]
    
    prompts = [
        "Make it brighter and more vibrant",
        "Add dramatic lighting",
        "Convert to black and white"
    ]
    
    results = await qwen_fast_edit_agent.batch_edit(images, prompts)
    
    for i, result in enumerate(results):
        if result["success"]:
            print(f"✅ Image {i+1}: {result['output_path']}")
        else:
            print(f"❌ Image {i+1}: {result['error']}")


async def example_custom_prompt():
    """Example: Custom prompt editing"""
    print("\n=== EXAMPLE 7: Custom Prompt ===")
    
    result = await qwen_fast_edit_agent.edit_image(
        image_path="uploads/photo.jpg",
        prompt="Remove the background and replace with a tropical beach scene",
        guidance_scale=1.2,
        num_inference_steps=10
    )
    
    if result["success"]:
        print(f"✅ Output: {result['output_path']}")


async def example_list_lora_styles():
    """Example: List available LoRA styles"""
    print("\n=== Available LoRA Styles ===")
    
    styles = qwen_lora_fusion_agent.list_lora_adapters()
    for name, description in styles.items():
        print(f"• {name}: {description}")


async def main():
    """Run all examples"""
    print("=" * 60)
    print("QWEN EDIT AGENTS - USAGE EXAMPLES")
    print("=" * 60)
    
    # List available LoRA styles
    await example_list_lora_styles()
    
    # Uncomment để chạy các example
    # await example_fast_edit()
    # await example_style_transfer()
    # await example_object_replacement()
    # await example_fashion_transfer()
    # await example_cinematic_edit()
    # await example_batch_edit()
    # await example_custom_prompt()
    
    print("\n" + "=" * 60)
    print("Done! Uncomment examples to test.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
