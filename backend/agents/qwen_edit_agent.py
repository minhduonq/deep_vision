"""
Qwen Image Edit Agent - Sử dụng Qwen-Image-Edit-2509 cho các tác vụ chỉnh sửa ảnh
"""
from gradio_client import Client, handle_file
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from loguru import logger
import asyncio
from functools import partial

class QwenEditAgent:
    """
    Agent sử dụng Qwen-Image-Edit-2509 cho image enhancement tasks
    """
    
    def __init__(self, use_fast: bool = False):
        """
        Args:
            use_fast: Nếu True, dùng Fast version (8 steps), False dùng Standard (40 steps)
        """
        self.use_fast = use_fast
        self.max_images = 10
        
        if use_fast:
            self.client = Client("linoyts/Qwen-Image-Edit-2509-Fast")
            self.default_steps = 8
            self.default_guidance = 1
            logger.info("Initialized Qwen Edit Agent (Fast mode)")
        else:
            self.client = Client("Qwen/Qwen-Image-Edit-2509")
            self.default_steps = 40
            self.default_guidance = 4
            logger.info("Initialized Qwen Edit Agent (Standard mode)")
    
    async def edit_image(
        self,
        image_path: Union[str, List[str]],
        prompt: str,
        seed: int = 0,
        randomize_seed: bool = True,
        guidance_scale: Optional[float] = None,
        num_steps: Optional[int] = None,
        height: int = 1024,
        width: int = 1024,
        rewrite_prompt: bool = True
    ) -> Dict[str, Any]:
        """
        Chỉnh sửa ảnh theo prompt (hỗ trợ 1 hoặc nhiều ảnh)
        
        Args:
            image_path: Đường dẫn ảnh input (str) hoặc list đường dẫn (tối đa 10 ảnh)
            prompt: Mô tả cách chỉnh sửa
            seed: Random seed
            randomize_seed: Có random seed không
            guidance_scale: Độ mạnh của guidance (None = dùng default)
            num_steps: Số bước inference (None = dùng default)
            height: Chiều cao output
            width: Chiều rộng output
            rewrite_prompt: Cho phép model viết lại prompt tốt hơn
            
        Returns:
            Dict chứa đường dẫn ảnh kết quả và metadata
        """
        try:
            # Handle single or multiple images
            image_paths = [image_path] if isinstance(image_path, str) else image_path
            
            if len(image_paths) > self.max_images:
                logger.warning(f"Too many images ({len(image_paths)}), limiting to {self.max_images}")
                image_paths = image_paths[:self.max_images]
            
            logger.info(f"Editing {len(image_paths)} image(s): {image_paths} with prompt: {prompt}")
            
            # Use default values if not specified
            guidance = guidance_scale if guidance_scale is not None else self.default_guidance
            steps = num_steps if num_steps is not None else self.default_steps
            
            # Prepare image files
            images = [handle_file(img_path) for img_path in image_paths]
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                partial(
                    self.client.predict,
                    images=images,
                    prompt=prompt,
                    seed=seed,
                    randomize_seed=randomize_seed,
                    true_guidance_scale=guidance,
                    num_inference_steps=steps,
                    height=height,
                    width=width,
                    rewrite_prompt=rewrite_prompt,
                    api_name="/infer"
                )
            )
            
            logger.success(f"Image(s) edited successfully: {result}")
            
            return {
                "success": True,
                "output_path": result,
                "num_images": len(image_paths),
                "metadata": {
                    "prompt": prompt,
                    "seed": seed,
                    "guidance_scale": guidance,
                    "steps": steps,
                    "resolution": f"{width}x{height}",
                    "model": "Fast" if self.use_fast else "Standard"
                }
            }
            
        except Exception as e:
            logger.error(f"Error editing image: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def edit_batch(
        self,
        image_paths: List[str],
        prompts: Union[str, List[str]],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Xử lý batch nhiều ảnh với các prompt khác nhau
        
        Args:
            image_paths: List đường dẫn ảnh
            prompts: Prompt chung (str) hoặc list prompts cho từng ảnh
            **kwargs: Các tham số khác cho edit_image
            
        Returns:
            List các kết quả
        """
        if isinstance(prompts, str):
            prompts = [prompts] * len(image_paths)
        
        if len(prompts) != len(image_paths):
            logger.error("Number of prompts must match number of images")
            return []
        
        tasks = []
        for img_path, prompt in zip(image_paths, prompts):
            tasks.append(self.edit_image(img_path, prompt, **kwargs))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def deblur(
        self, 
        image_path: Union[str, List[str]],
        strength: str = "medium"
    ) -> Dict[str, Any]:
        """
        Làm sắc nét ảnh bị mờ (hỗ trợ nhiều ảnh)
        
        Args:
            image_path: Đường dẫn ảnh hoặc list đường dẫn
            strength: "light", "medium", "strong"
        """
        prompts = {
            "light": "Slightly sharpen this image, enhance clarity and details",
            "medium": "Remove blur and make this image sharp and clear, enhance all details",
            "strong": "Significantly enhance sharpness, remove all blur, maximize clarity and detail"
        }
        
        prompt = prompts.get(strength, prompts["medium"])
        return await self.edit_image(image_path, prompt)
    
    async def remove_object(
        self,
        image_path: Union[str, List[str]],
        object_description: str
    ) -> Dict[str, Any]:
        """
        Xóa object khỏi ảnh (hỗ trợ nhiều ảnh)
        
        Args:
            image_path: Đường dẫn ảnh hoặc list đường dẫn
            object_description: Mô tả object cần xóa (ví dụ: "the person in red shirt")
        """
        prompt = f"Remove {object_description} from this image, fill the area naturally and seamlessly"
        return await self.edit_image(image_path, prompt)
    
    async def beauty_enhance(
        self,
        image_path: Union[str, List[str]],
        level: str = "natural"
    ) -> Dict[str, Any]:
        """
        Làm đẹp khuôn mặt (hỗ trợ nhiều ảnh)
        
        Args:
            image_path: Đường dẫn ảnh hoặc list đường dẫn
            level: "subtle", "natural", "strong"
        """
        prompts = {
            "subtle": "Subtly enhance facial features, smooth skin tone naturally, maintain authenticity",
            "natural": "Enhance facial beauty naturally, smooth skin, brighten eyes, perfect lighting",
            "strong": "Professional beauty enhancement, flawless skin, perfect features, magazine quality"
        }
        
        prompt = prompts.get(level, prompts["natural"])
        return await self.edit_image(image_path, prompt)
    
    async def style_transfer(
        self,
        image_path: Union[str, List[str]],
        style: str
    ) -> Dict[str, Any]:
        """
        Chuyển đổi style ảnh (hỗ trợ nhiều ảnh)
        
        Args:
            image_path: Đường dẫn ảnh hoặc list đường dẫn
            style: Mô tả style (ví dụ: "oil painting", "anime", "watercolor")
        """
        prompt = f"Transform this image into {style} style, maintain composition and subjects"
        return await self.edit_image(image_path, prompt)
    
    async def upscale_and_enhance(
        self,
        image_path: Union[str, List[str]],
        target_size: tuple = (2048, 2048)
    ) -> Dict[str, Any]:
        """
        Upscale và enhance ảnh (hỗ trợ nhiều ảnh)
        """
        prompt = "Upscale this image, enhance quality, sharpen details, improve colors"
        return await self.edit_image(
            image_path, 
            prompt,
            height=target_size[1],
            width=target_size[0]
        )


# Singleton instance
qwen_edit_agent = QwenEditAgent(use_fast=False)
qwen_edit_agent_fast = QwenEditAgent(use_fast=True)