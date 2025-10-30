"""Prompt processor for analyzing and routing image editing tasks."""

from PIL import Image
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PromptProcessor:
    """
    Processes user prompts and routes to appropriate image editing models.
    
    This class analyzes the prompt to determine the type of edit requested
    and applies the appropriate model/technique.
    """
    
    def __init__(self, device: str = "cpu"):
        """
        Initialize the prompt processor.
        
        Args:
            device: Device to use for inference
        """
        self.device = device
        self._models_loaded = False
        self._instruct_pix2pix = None
        self._inpainting_model = None
        
        logger.info(f"PromptProcessor initialized on {device}")
    
    def _load_instruct_pix2pix(self):
        """Lazy load InstructPix2Pix model for general image editing."""
        if self._instruct_pix2pix is None:
            try:
                import torch
                from diffusers import StableDiffusionInstructPix2PixPipeline
                
                logger.info("Loading InstructPix2Pix model...")
                self._instruct_pix2pix = StableDiffusionInstructPix2PixPipeline.from_pretrained(
                    "timbrooks/instruct-pix2pix",
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    safety_checker=None,
                )
                self._instruct_pix2pix.to(self.device)
                
                # Enable memory optimizations
                if self.device == "cuda":
                    self._instruct_pix2pix.enable_attention_slicing()
                    
                logger.info("InstructPix2Pix model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load InstructPix2Pix model: {e}")
                raise
                
        return self._instruct_pix2pix
    
    def _load_inpainting_model(self):
        """Lazy load Stable Diffusion Inpainting model for object removal."""
        if self._inpainting_model is None:
            try:
                import torch
                from diffusers import StableDiffusionInpaintPipeline
                
                logger.info("Loading Inpainting model...")
                self._inpainting_model = StableDiffusionInpaintPipeline.from_pretrained(
                    "runwayml/stable-diffusion-inpainting",
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    safety_checker=None,
                )
                self._inpainting_model.to(self.device)
                
                # Enable memory optimizations
                if self.device == "cuda":
                    self._inpainting_model.enable_attention_slicing()
                    
                logger.info("Inpainting model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Inpainting model: {e}")
                raise
                
        return self._inpainting_model
    
    def _analyze_prompt(self, prompt: str) -> str:
        """
        Analyze the prompt to determine the editing type.
        
        Args:
            prompt: User's text prompt
            
        Returns:
            Editing type: 'remove', 'inpaint', 'sharpen', 'add', 'beautify', or 'general'
        """
        prompt_lower = prompt.lower()
        
        # Check for beautification first (before 'add' to handle 'add makeup')
        if any(word in prompt_lower for word in ['beautify', 'beauty', 'makeup', 'smooth skin']):
            return 'beautify'
        
        # Check for removal/inpainting
        if any(word in prompt_lower for word in ['remove', 'delete', 'erase', 'clean']):
            return 'remove'
        
        # Check for sharpening
        if any(word in prompt_lower for word in ['sharpen', 'sharp', 'crisp', 'detail', 'enhance details']):
            return 'sharpen'
        
        # Check for adding objects
        if any(word in prompt_lower for word in ['add', 'insert', 'place', 'put']):
            return 'add'
        
        return 'general'
    
    def process(
        self,
        image: Image.Image,
        prompt: str,
        negative_prompt: Optional[str] = None,
        strength: float = 0.75,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 50,
        seed: Optional[int] = None,
    ) -> Image.Image:
        """
        Process the image according to the prompt.
        
        Args:
            image: Input PIL Image
            prompt: Text description of desired edit
            negative_prompt: Things to avoid
            strength: Transformation strength
            guidance_scale: How closely to follow prompt
            num_inference_steps: Number of denoising steps
            seed: Random seed
            
        Returns:
            Edited PIL Image
        """
        # Set random seed if provided
        if seed is not None:
            try:
                import torch
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed(seed)
            except ImportError:
                import random
                import numpy as np
                random.seed(seed)
                np.random.seed(seed)
        
        # Analyze prompt type
        edit_type = self._analyze_prompt(prompt)
        logger.info(f"Detected edit type: {edit_type}")
        
        # Route to appropriate processing method
        if edit_type in ['remove', 'add', 'general', 'sharpen', 'beautify']:
            # Use InstructPix2Pix for most editing tasks
            return self._process_with_instruct_pix2pix(
                image=image,
                prompt=prompt,
                negative_prompt=negative_prompt,
                guidance_scale=guidance_scale,
                image_guidance_scale=1.5,
                num_inference_steps=num_inference_steps,
            )
        else:
            # Fallback to general editing
            return self._process_with_instruct_pix2pix(
                image=image,
                prompt=prompt,
                negative_prompt=negative_prompt,
                guidance_scale=guidance_scale,
                image_guidance_scale=1.5,
                num_inference_steps=num_inference_steps,
            )
    
    def _process_with_instruct_pix2pix(
        self,
        image: Image.Image,
        prompt: str,
        negative_prompt: Optional[str],
        guidance_scale: float,
        image_guidance_scale: float,
        num_inference_steps: int,
    ) -> Image.Image:
        """Process image using InstructPix2Pix model."""
        pipeline = self._load_instruct_pix2pix()
        
        # Resize image if too large
        max_size = 512
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Resized image to {new_size}")
        
        # Generate edited image
        result = pipeline(
            prompt=prompt,
            image=image,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            image_guidance_scale=image_guidance_scale,
            num_inference_steps=num_inference_steps,
        )
        
        return result.images[0]
