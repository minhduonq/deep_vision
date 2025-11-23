"""
Replicate API Wrapper for Image Processing Models
Handles all interactions with Replicate API for image enhancement and generation
"""

import replicate
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
from PIL import Image
import requests
from io import BytesIO

from backend.core.config import settings


class ReplicateWrapper:
    """Wrapper for Replicate API calls"""
    
    def __init__(self):
        self.client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)
        logger.info("Replicate client initialized")
    
    async def inpaint_image(
        self,
        image_path: Path,
        mask_path: Optional[Path] = None,
        prompt: Optional[str] = None
    ) -> Path:
        """
        Remove objects from image using LaMa inpainting model
        
        Args:
            image_path: Path to input image
            mask_path: Path to mask image (white = remove, black = keep)
            prompt: Optional text prompt for guided inpainting
            
        Returns:
            Path to processed image
        """
        try:
            logger.info(f"Starting inpainting for {image_path}")
            
            # Use LaMa model for inpainting
            # https://replicate.com/lucataco/lama
            model_version = "lucataco/lama:b1e57e8c559baf0eb0bfbf9b6c1b2c38c94a76bffb1b69c9cadb38a6d4285b77"
            
            with open(image_path, "rb") as image_file:
                input_params = {
                    "image": image_file,
                }
                
                # Add mask if provided
                if mask_path and mask_path.exists():
                    with open(mask_path, "rb") as mask_file:
                        input_params["mask"] = mask_file
                
                # Run the model
                output = self.client.run(
                    model_version,
                    input=input_params
                )
            
            # Download result
            output_path = image_path.parent.parent / "outputs" / f"inpaint_{image_path.name}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(output, str):
                # Download from URL
                response = requests.get(output)
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                    
                logger.info(f"Inpainting completed: {output_path}")
                return output_path
            else:
                logger.error(f"Unexpected output type: {type(output)}")
                raise ValueError("Invalid output from Replicate")
                
        except Exception as e:
            logger.error(f"Inpainting error: {e}")
            raise
    
    async def deblur_image(self, image_path: Path) -> Path:
        """
        Deblur image using SwinIR model
        
        Args:
            image_path: Path to input image
            
        Returns:
            Path to deblurred image
        """
        try:
            logger.info(f"Starting deblur for {image_path}")
            
            # Use NAFNet or SwinIR for deblurring
            # https://replicate.com/jingyunliang/swinir
            model_version = "jingyunliang/swinir:660d922d33153019e8c594a6ea8c64f77d58f35093c93e7a73ec38f0cb9c7b21"
            
            with open(image_path, "rb") as image_file:
                output = self.client.run(
                    model_version,
                    input={
                        "image": image_file,
                        "task_type": "real_sr",  # Real-world image super-resolution
                        "scale": 2
                    }
                )
            
            # Download result
            output_path = image_path.parent.parent / "outputs" / f"deblur_{image_path.name}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(output, str):
                response = requests.get(output)
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                    
                logger.info(f"Deblur completed: {output_path}")
                return output_path
            else:
                logger.error(f"Unexpected output type: {type(output)}")
                raise ValueError("Invalid output from Replicate")
                
        except Exception as e:
            logger.error(f"Deblur error: {e}")
            raise
    
    async def enhance_beauty(self, image_path: Path) -> Path:
        """
        Enhance portrait beauty using GFPGAN
        
        Args:
            image_path: Path to input image
            
        Returns:
            Path to enhanced image
        """
        try:
            logger.info(f"Starting beauty enhancement for {image_path}")
            
            # Use GFPGAN for face restoration
            # https://replicate.com/tencentarc/gfpgan
            model_version = "tencentarc/gfpgan:9283608cc6b7be6b65a8e44983db012355fde4132009bf99d976b2f0896856a3"
            
            with open(image_path, "rb") as image_file:
                output = self.client.run(
                    model_version,
                    input={
                        "img": image_file,
                        "version": "v1.4",
                        "scale": 2
                    }
                )
            
            # Download result
            output_path = image_path.parent.parent / "outputs" / f"beauty_{image_path.name}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(output, str):
                response = requests.get(output)
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                    
                logger.info(f"Beauty enhancement completed: {output_path}")
                return output_path
            else:
                logger.error(f"Unexpected output type: {type(output)}")
                raise ValueError("Invalid output from Replicate")
                
        except Exception as e:
            logger.error(f"Beauty enhancement error: {e}")
            raise
    
    async def generate_image(self, prompt: str, **kwargs) -> Path:
        """
        Generate image from text prompt using SDXL
        
        Args:
            prompt: Text description of desired image
            **kwargs: Additional parameters (negative_prompt, num_inference_steps, etc.)
            
        Returns:
            Path to generated image
        """
        try:
            logger.info(f"Starting image generation: {prompt[:50]}...")
            
            # Use Stable Diffusion XL
            # https://replicate.com/stability-ai/sdxl
            model_version = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
            
            output = self.client.run(
                model_version,
                input={
                    "prompt": prompt,
                    "negative_prompt": kwargs.get("negative_prompt", "ugly, blurry, low quality"),
                    "num_inference_steps": kwargs.get("num_inference_steps", 50),
                    "guidance_scale": kwargs.get("guidance_scale", 7.5),
                    "width": kwargs.get("width", 1024),
                    "height": kwargs.get("height", 1024),
                }
            )
            
            # Download result
            output_dir = settings.OUTPUT_DIR
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"generated_{prompt[:30].replace(' ', '_')}.png"
            
            if isinstance(output, list) and len(output) > 0:
                response = requests.get(output[0])
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                    
                logger.info(f"Image generation completed: {output_path}")
                return output_path
            else:
                logger.error(f"Unexpected output type: {type(output)}")
                raise ValueError("Invalid output from Replicate")
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            raise


# Global instance
replicate_client = ReplicateWrapper()
