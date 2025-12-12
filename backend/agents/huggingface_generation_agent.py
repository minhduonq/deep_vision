"""
HuggingFace Generation Agent - Sử dụng Z-Image-Turbo cho text-to-image generation
"""
from gradio_client import Client, handle_file
from typing import Optional, Dict, Any, List
from loguru import logger
import asyncio
from functools import partial

class HuggingFaceGenerationAgent:
    """
    Agent sử dụng Tongyi-MAI/Z-Image-Turbo cho image generation
    """
    
    RESOLUTIONS = {
        "square": "1024x1024 ( 1:1 )",
        "portrait": "768x1024 ( 3:4 )",
        "landscape": "1024x768 ( 4:3 )",
        "wide": "1280x720 ( 16:9 )",
        "ultrawide": "1920x1080 ( 16:9 )"
    }
    
    def __init__(self):
        """Initialize HuggingFace client (lazy loading)"""
        self._client = None
        logger.info("Initialized HuggingFace Generation Agent (Z-Image-Turbo)")
    
    def _get_client(self):
        """Get or create Gradio client (lazy loading)"""
        if self._client is None:
            logger.info("Connecting to HuggingFace Space...")
            self._client = Client("Tongyi-MAI/Z-Image-Turbo")
            logger.success("Connected to Z-Image-Turbo Space")
        return self._client
    
    async def generate_image(
        self,
        prompt: str,
        resolution: str = "square",
        seed: int = 42,
        steps: int = 8,
        shift: float = 3.0,
        random_seed: bool = True,
        gallery_images: List[str] = []
    ) -> Dict[str, Any]:
        """
        Generate image từ text prompt
        
        Args:
            prompt: Mô tả ảnh cần tạo
            resolution: "square", "portrait", "landscape", "wide", "ultrawide"
            seed: Random seed
            steps: Số bước inference (4-12, default 8 cho speed/quality balance)
            shift: Shift parameter (0-10, default 3)
            random_seed: Có random seed không
            gallery_images: Reference images (optional)
            
        Returns:
            Dict chứa đường dẫn ảnh kết quả và metadata
        """
        try:
            logger.info(f"Generating image with prompt: {prompt}")
            
            # Convert resolution key to actual resolution string
            resolution_str = self.RESOLUTIONS.get(resolution, self.RESOLUTIONS["square"])
            
            # Run in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                partial(
                    self._get_client().predict,
                    prompt=prompt,
                    resolution=resolution_str,
                    seed=seed,
                    steps=steps,
                    shift=shift,
                    random_seed=random_seed,
                    gallery_images=gallery_images,
                    api_name="/generate"
                )
            )
            
            logger.success(f"Image generated successfully: {result}")
            logger.debug(f"Result type: {type(result)}, content: {result}")
            
            # Gradio client returns complex structure: ([{'image': 'path', 'caption': None}], seed, ...)
            # Extract the actual file path
            output_path = None
            
            if isinstance(result, (tuple, list)):
                # Get first element (list of results)
                first_elem = result[0] if result else None
                
                if isinstance(first_elem, (list, tuple)) and first_elem:
                    # Get first result from list
                    first_result = first_elem[0]
                    
                    if isinstance(first_result, dict) and 'image' in first_result:
                        # Extract image path from dict
                        output_path = first_result['image']
                    elif isinstance(first_result, str):
                        # Direct string path
                        output_path = first_result
                    else:
                        output_path = first_result
                elif isinstance(first_elem, str):
                    # Direct string path
                    output_path = first_elem
                else:
                    output_path = first_elem
            else:
                output_path = result
            
            logger.info(f"Extracted output path: {output_path}")
            
            return {
                "success": True,
                "output_path": output_path,
                "metadata": {
                    "prompt": prompt,
                    "resolution": resolution_str,
                    "seed": seed,
                    "steps": steps,
                    "shift": shift,
                    "model": "Z-Image-Turbo"
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_variations(
        self,
        prompt: str,
        num_variations: int = 4,
        resolution: str = "square"
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple variations của cùng một prompt
        """
        results = []
        for i in range(num_variations):
            result = await self.generate_image(
                prompt=prompt,
                resolution=resolution,
                random_seed=True,
                seed=i
            )
            results.append(result)
        
        return results
    
    async def generate_with_style(
        self,
        subject: str,
        style: str,
        resolution: str = "square"
    ) -> Dict[str, Any]:
        """
        Generate image với specific style
        
        Args:
            subject: Chủ thể chính (ví dụ: "a cat")
            style: Style mong muốn (ví dụ: "oil painting", "anime", "photorealistic")
        """
        prompt = f"{subject} in {style} style, high quality, detailed"
        return await self.generate_image(prompt, resolution)
    
    async def generate_scene(
        self,
        scene_description: str,
        mood: Optional[str] = None,
        time_of_day: Optional[str] = None,
        resolution: str = "landscape"
    ) -> Dict[str, Any]:
        """
        Generate scene với mood và lighting
        
        Args:
            scene_description: Mô tả scene
            mood: "peaceful", "dramatic", "mysterious", etc.
            time_of_day: "sunrise", "noon", "sunset", "night"
        """
        prompt = scene_description
        
        if mood:
            prompt += f", {mood} mood"
        
        if time_of_day:
            prompt += f", {time_of_day} lighting"
        
        prompt += ", cinematic, high quality"
        
        return await self.generate_image(prompt, resolution)


# Singleton instance
generation_agent = HuggingFaceGenerationAgent()