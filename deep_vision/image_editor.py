"""Main image editor class that handles prompt-based image editing."""

from PIL import Image
import numpy as np
from typing import Optional, Union, List
import logging

from .models.prompt_processor import PromptProcessor
from .utils.image_utils import ImageProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageEditor:
    """
    Main class for image editing based on user prompts.
    
    Supports various editing operations:
    - Object removal (inpainting)
    - Image sharpening
    - Object addition
    - Beauty enhancement
    - And more based on prompt
    """
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize the ImageEditor.
        
        Args:
            device: Device to use ('cuda', 'cpu', or None for auto-detection)
        """
        if device is None:
            try:
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self.device = "cpu"
        else:
            self.device = device
            
        logger.info(f"Initializing ImageEditor on device: {self.device}")
        
        self.prompt_processor = PromptProcessor(device=self.device)
        self.image_processor = ImageProcessor()
        
    def edit_image(
        self,
        image: Union[str, Image.Image, np.ndarray],
        prompt: str,
        negative_prompt: Optional[str] = None,
        strength: float = 0.75,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 50,
        seed: Optional[int] = None,
    ) -> Image.Image:
        """
        Edit an image based on a text prompt.
        
        Args:
            image: Input image (path, PIL Image, or numpy array)
            prompt: Text description of the desired edit
            negative_prompt: Things to avoid in the output
            strength: How much to transform the image (0.0 to 1.0)
            guidance_scale: How closely to follow the prompt
            num_inference_steps: Number of denoising steps
            seed: Random seed for reproducibility
            
        Returns:
            Edited PIL Image
        """
        # Load and preprocess image
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image).convert("RGB")
        elif not isinstance(image, Image.Image):
            raise ValueError("Image must be a path, PIL Image, or numpy array")
            
        logger.info(f"Editing image with prompt: '{prompt}'")
        
        # Process based on prompt type
        edited_image = self.prompt_processor.process(
            image=image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            seed=seed,
        )
        
        return edited_image
    
    def remove_object(
        self,
        image: Union[str, Image.Image, np.ndarray],
        object_description: str,
        **kwargs
    ) -> Image.Image:
        """
        Remove an object from the image.
        
        Args:
            image: Input image
            object_description: Description of object to remove
            **kwargs: Additional parameters for edit_image
            
        Returns:
            Image with object removed
        """
        prompt = f"remove {object_description}, clean background, natural inpainting"
        return self.edit_image(image, prompt, **kwargs)
    
    def sharpen_image(
        self,
        image: Union[str, Image.Image, np.ndarray],
        intensity: str = "medium",
        **kwargs
    ) -> Image.Image:
        """
        Sharpen the image.
        
        Args:
            image: Input image
            intensity: Sharpening intensity (low, medium, high)
            **kwargs: Additional parameters for edit_image
            
        Returns:
            Sharpened image
        """
        prompt = f"{intensity} sharpening, enhanced details, crisp, clear, high quality"
        return self.edit_image(image, prompt, **kwargs)
    
    def add_object(
        self,
        image: Union[str, Image.Image, np.ndarray],
        object_description: str,
        location: Optional[str] = None,
        **kwargs
    ) -> Image.Image:
        """
        Add an object to the image.
        
        Args:
            image: Input image
            object_description: Description of object to add
            location: Where to add the object (e.g., "in the center", "on the left")
            **kwargs: Additional parameters for edit_image
            
        Returns:
            Image with object added
        """
        if location:
            prompt = f"add {object_description} {location}, natural, realistic, high quality"
        else:
            prompt = f"add {object_description}, natural, realistic, high quality"
        return self.edit_image(image, prompt, **kwargs)
    
    def beautify(
        self,
        image: Union[str, Image.Image, np.ndarray],
        features: Optional[List[str]] = None,
        **kwargs
    ) -> Image.Image:
        """
        Apply beauty enhancement to the image.
        
        Args:
            image: Input image
            features: Specific features to enhance (e.g., ["skin", "eyes", "teeth"])
            **kwargs: Additional parameters for edit_image
            
        Returns:
            Beautified image
        """
        if features:
            feature_str = ", ".join(features)
            prompt = f"beautify, enhance {feature_str}, smooth skin, natural beauty, high quality"
        else:
            prompt = "beautify, enhance facial features, smooth skin, bright eyes, natural beauty, high quality"
        return self.edit_image(image, prompt, **kwargs)
