"""Advanced integration example showing how to use Deep Vision in a real application."""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image

from deep_vision import ImageEditor


class ImageEditingService:
    """
    A service class demonstrating how to integrate Deep Vision into an application.
    
    This example shows:
    - Batch processing
    - Configuration management
    - Error handling
    - Progress tracking
    - Result caching
    """
    
    def __init__(
        self,
        device: str = "auto",
        output_dir: str = "edited_images",
        cache_dir: str = ".cache"
    ):
        """Initialize the image editing service."""
        self.editor = ImageEditor(device=device)
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Load history
        self.history_file = self.cache_dir / "history.json"
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load editing history from cache."""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save editing history to cache."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def edit_single(
        self,
        image_path: str,
        prompt: str,
        output_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Edit a single image.
        
        Args:
            image_path: Path to input image
            prompt: Editing prompt
            output_name: Optional custom output name
            **kwargs: Additional parameters for edit_image
            
        Returns:
            Path to edited image
        """
        # Generate output path
        if output_name is None:
            input_name = Path(image_path).stem
            output_name = f"{input_name}_edited.jpg"
        
        output_path = self.output_dir / output_name
        
        # Edit the image
        print(f"Editing {image_path}...")
        print(f"Prompt: {prompt}")
        
        try:
            result = self.editor.edit_image(
                image=image_path,
                prompt=prompt,
                **kwargs
            )
            
            # Save result
            result.save(str(output_path))
            
            # Record in history
            self.history.append({
                "input": image_path,
                "output": str(output_path),
                "prompt": prompt,
                "parameters": kwargs
            })
            self._save_history()
            
            print(f"Saved to {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"Error editing {image_path}: {e}")
            raise
    
    def batch_edit(
        self,
        image_prompts: Dict[str, str],
        **common_kwargs
    ) -> Dict[str, str]:
        """
        Edit multiple images with different prompts.
        
        Args:
            image_prompts: Dictionary mapping image paths to prompts
            **common_kwargs: Common parameters for all edits
            
        Returns:
            Dictionary mapping input paths to output paths
        """
        results = {}
        total = len(image_prompts)
        
        for i, (image_path, prompt) in enumerate(image_prompts.items(), 1):
            print(f"\n[{i}/{total}] Processing {image_path}...")
            
            try:
                output_path = self.edit_single(
                    image_path=image_path,
                    prompt=prompt,
                    **common_kwargs
                )
                results[image_path] = output_path
            except Exception as e:
                print(f"Failed to process {image_path}: {e}")
                results[image_path] = None
        
        return results
    
    def apply_preset(
        self,
        image_path: str,
        preset_name: str,
        **kwargs
    ) -> str:
        """
        Apply a predefined editing preset.
        
        Args:
            image_path: Path to input image
            preset_name: Name of the preset
            **kwargs: Override preset parameters
            
        Returns:
            Path to edited image
        """
        # Define presets
        presets = {
            "vibrant": {
                "prompt": "vibrant colors, enhanced saturation, vivid",
                "negative_prompt": "dull, washed out",
                "guidance_scale": 7.5,
            },
            "professional": {
                "prompt": "professional photography, high quality, sharp details",
                "negative_prompt": "blurry, amateur, low quality",
                "guidance_scale": 8.0,
            },
            "vintage": {
                "prompt": "vintage style, film grain, warm tones, nostalgic",
                "negative_prompt": "modern, digital, cold",
                "guidance_scale": 7.0,
            },
            "dramatic": {
                "prompt": "dramatic lighting, high contrast, cinematic",
                "negative_prompt": "flat, boring",
                "guidance_scale": 8.5,
            },
            "clean": {
                "prompt": "clean, minimalist, simple background",
                "negative_prompt": "cluttered, busy, complex",
                "guidance_scale": 7.5,
            }
        }
        
        if preset_name not in presets:
            raise ValueError(f"Unknown preset: {preset_name}")
        
        # Merge preset with kwargs
        params = {**presets[preset_name], **kwargs}
        
        # Generate output name with preset
        input_name = Path(image_path).stem
        output_name = f"{input_name}_{preset_name}.jpg"
        
        return self.edit_single(
            image_path=image_path,
            output_name=output_name,
            **params
        )
    
    def create_variations(
        self,
        image_path: str,
        prompt: str,
        num_variations: int = 3,
        **kwargs
    ) -> List[str]:
        """
        Create multiple variations of the same edit using different seeds.
        
        Args:
            image_path: Path to input image
            prompt: Editing prompt
            num_variations: Number of variations to create
            **kwargs: Additional parameters
            
        Returns:
            List of paths to variation images
        """
        variations = []
        input_name = Path(image_path).stem
        
        for i in range(num_variations):
            seed = 1000 + i  # Use different seeds
            output_name = f"{input_name}_var{i+1}.jpg"
            
            print(f"Creating variation {i+1}/{num_variations}...")
            
            output_path = self.edit_single(
                image_path=image_path,
                prompt=prompt,
                output_name=output_name,
                seed=seed,
                **kwargs
            )
            variations.append(output_path)
        
        return variations
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent editing history."""
        return self.history[-limit:]
    
    def clear_cache(self):
        """Clear cache and history."""
        if self.history_file.exists():
            self.history_file.unlink()
        self.history = []
        print("Cache cleared")


def example_basic_integration():
    """Example: Basic service usage."""
    print("=== Basic Integration Example ===\n")
    
    service = ImageEditingService(device="cpu")
    
    # Single edit
    # service.edit_single(
    #     image_path="input.jpg",
    #     prompt="make the sky blue and vibrant",
    #     guidance_scale=7.5
    # )
    
    print("Single image edited successfully!")


def example_batch_processing():
    """Example: Batch processing multiple images."""
    print("\n=== Batch Processing Example ===\n")
    
    service = ImageEditingService(device="cpu")
    
    # Define batch edits
    batch_edits = {
        "photo1.jpg": "enhance colors and brightness",
        "photo2.jpg": "remove watermark from corner",
        "photo3.jpg": "make sharper and clearer",
    }
    
    # Process batch
    # results = service.batch_edit(
    #     image_prompts=batch_edits,
    #     num_inference_steps=50
    # )
    
    print("Batch processing demonstration complete!")


def example_presets():
    """Example: Using predefined presets."""
    print("\n=== Presets Example ===\n")
    
    service = ImageEditingService(device="cpu")
    
    # Apply different presets to the same image
    presets = ["vibrant", "professional", "vintage", "dramatic", "clean"]
    
    for preset in presets:
        print(f"Applying '{preset}' preset...")
        # service.apply_preset(
        #     image_path="input.jpg",
        #     preset_name=preset
        # )
    
    print("Presets demonstration complete!")


def example_variations():
    """Example: Creating multiple variations."""
    print("\n=== Variations Example ===\n")
    
    service = ImageEditingService(device="cpu")
    
    # Create 3 variations
    # variations = service.create_variations(
    #     image_path="input.jpg",
    #     prompt="beautiful sunset scene with warm colors",
    #     num_variations=3,
    #     guidance_scale=7.5
    # )
    
    print("Variations demonstration complete!")


def example_workflow():
    """Example: Complete workflow with multiple steps."""
    print("\n=== Complete Workflow Example ===\n")
    
    service = ImageEditingService(device="cpu")
    
    # Step 1: Clean up the image
    print("Step 1: Cleaning up...")
    # cleaned = service.edit_single(
    #     image_path="input.jpg",
    #     prompt="remove noise and artifacts, clean image",
    #     output_name="step1_cleaned.jpg"
    # )
    
    # Step 2: Enhance colors
    print("Step 2: Enhancing colors...")
    # enhanced = service.edit_single(
    #     image_path=cleaned,
    #     prompt="vibrant colors, rich tones",
    #     output_name="step2_enhanced.jpg"
    # )
    
    # Step 3: Final touch
    print("Step 3: Final touches...")
    # final = service.edit_single(
    #     image_path=enhanced,
    #     prompt="professional photography, high quality",
    #     output_name="final_result.jpg"
    # )
    
    print("Workflow demonstration complete!")


if __name__ == "__main__":
    print("Deep Vision Advanced Integration Examples")
    print("=" * 50)
    
    # Note: Uncomment the service calls in each example to actually run them
    # Make sure you have input images in the current directory
    
    example_basic_integration()
    example_batch_processing()
    example_presets()
    example_variations()
    example_workflow()
    
    print("\n" + "=" * 50)
    print("All examples demonstrated!")
    print("\nTo run these examples with actual images:")
    print("1. Uncomment the service calls in each example function")
    print("2. Provide input images (e.g., input.jpg, photo1.jpg, etc.)")
    print("3. Run this script again")
