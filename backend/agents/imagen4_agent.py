"""
Imagen 4 Agent - Sử dụng Google Imagen 4 từ Replicate cho text-to-image generation nhanh
"""
import replicate
from pathlib import Path
from typing import Optional, Dict, Any, List
from loguru import logger
import asyncio
from functools import partial
import os

class Imagen4Agent:
    """
    Agent sử dụng Google Imagen 4 (Imagen 3 Fast) từ Replicate cho image generation
    Imagen 4 có tốc độ nhanh hơn và chất lượng cao
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Args:
            api_token: Replicate API token (hoặc set qua env var REPLICATE_API_TOKEN)
        """
        # Load token from argument or environment
        if api_token:
            os.environ["REPLICATE_API_TOKEN"] = api_token
        elif not os.environ.get("REPLICATE_API_TOKEN"):
            logger.error("REPLICATE_API_TOKEN not found in environment!")
        
        # Verify token is set
        token = os.environ.get("REPLICATE_API_TOKEN", "")
        if token:
            logger.info(f"Replicate API token loaded: {token[:10]}...{token[-4:]}")
        
        self.model_version = "google/imagen-4"
        logger.info("Initialized Imagen 4 Agent (Google Imagen 4)")
    
    def _calculate_aspect_ratio(self, width: int, height: int) -> str:
        """
        Convert width/height to closest supported aspect ratio
        Supported: "1:1", "9:16", "16:9", "3:4", "4:3"
        """
        ratio = width / height
        
        # Map to closest supported aspect ratio
        if abs(ratio - 1.0) < 0.15:  # Close to square
            return "1:1"
        elif ratio < 0.7:  # Portrait, tall
            return "9:16"
        elif ratio > 1.5:  # Landscape, wide
            return "16:9"
        elif ratio < 1.0:  # Portrait
            return "3:4"
        else:  # Landscape
            return "4:3"
    
    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        negative_prompt: str = "",
        seed: Optional[int] = None,
        output_format: str = "png",
        output_quality: int = 90
    ) -> Dict[str, Any]:
        """
        Generate image từ text prompt sử dụng Imagen 4
        
        Args:
            prompt: Mô tả ảnh cần tạo
            width: Chiều rộng ảnh (sẽ convert sang aspect ratio gần nhất)
            height: Chiều cao ảnh (sẽ convert sang aspect ratio gần nhất)
            negative_prompt: Những gì không muốn trong ảnh
            seed: Random seed
            output_format: "png" hoặc "jpg"
            output_quality: Chất lượng output (1-100)
            
        Returns:
            Dict chứa đường dẫn ảnh kết quả và metadata
        """
        try:
            logger.info(f"Generating image with Imagen 4: {prompt[:50]}...")
            
            # Convert to supported aspect ratio
            aspect_ratio = self._calculate_aspect_ratio(width, height)
            logger.info(f"Using aspect ratio: {aspect_ratio} (requested {width}x{height})")
            
            input_dict = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "output_format": output_format,
                "output_quality": output_quality
            }
            
            if seed is not None:
                input_dict["seed"] = seed
            
            if negative_prompt:
                input_dict["negative_prompt"] = negative_prompt
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(
                None,
                partial(
                    replicate.run,
                    self.model_version,
                    input=input_dict
                )
            )
            
            logger.success(f"Image generated successfully with Imagen 4")
            
            # Replicate returns URL or list of URLs
            output_path = output[0] if isinstance(output, list) else output
            
            return {
                "success": True,
                "output_path": output_path,
                "metadata": {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "aspect_ratio": aspect_ratio,
                    "width": width,
                    "height": height,
                    "seed": seed,
                    "model": "imagen-4",
                    "output_format": output_format,
                    "output_quality": output_quality
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating image with Imagen 4: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
imagen4_agent = Imagen4Agent()
