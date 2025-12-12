"""
Qwen Fast Edit Agent - Single image editing with fast inference
Sử dụng multimodalart/Qwen-Image-Edit-Fast
"""
from gradio_client import Client, handle_file
from pathlib import Path
from typing import Optional, Dict, Any, Union
from loguru import logger
import asyncio
from functools import partial
import os


class QwenFastEditAgent:
    """
    Agent chuyên dùng cho single image editing với tốc độ nhanh
    Phù hợp cho: color correction, style changes, simple edits
    """
    
    def __init__(self):
        """Initialize Qwen Fast Edit client"""
        self._client = None
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        logger.info("Initialized Qwen Fast Edit Agent")
    
    def _get_client(self):
        """Get or create Gradio client (lazy loading)"""
        if self._client is None:
            logger.info("Connecting to Qwen-Image-Edit-Fast Space...")
            self._client = Client(
                "multimodalart/Qwen-Image-Edit-Fast",
                hf_token=self.hf_token
            )
            logger.success("Connected to Qwen-Image-Edit-Fast Space")
        return self._client
    
    async def edit_image(
        self,
        image_path: str,
        prompt: str,
        seed: int = 0,
        randomize_seed: bool = True,
        guidance_scale: float = 1.0,
        num_inference_steps: int = 8,
        rewrite_prompt: bool = True
    ) -> Dict[str, Any]:
        """
        Fast edit cho single image
        
        Args:
            image_path: Đường dẫn ảnh input
            prompt: Mô tả chỉnh sửa (ví dụ: "Change the color to red")
            seed: Random seed (0 = random)
            randomize_seed: Tự động random seed
            guidance_scale: Độ mạnh của prompt (0.5-2.0, default 1.0)
            num_inference_steps: Số bước inference (4-12, default 8)
            rewrite_prompt: Cho phép AI viết lại prompt tốt hơn
            
        Returns:
            Dict chứa output_path và metadata
        """
        try:
            logger.info(f"Fast editing image: {image_path}")
            logger.info(f"Prompt: {prompt}")
            
            # Validate image path
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Run prediction
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                partial(
                    self._get_client().predict,
                    image=handle_file(image_path),
                    prompt=prompt,
                    seed=seed,
                    randomize_seed=randomize_seed,
                    true_guidance_scale=guidance_scale,
                    num_inference_steps=num_inference_steps,
                    rewrite_prompt=rewrite_prompt,
                    api_name="/infer"
                )
            )
            
            # Result is tuple: (image_path, seed_used)
            output_path, used_seed = result
            
            logger.success(f"Image edited successfully: {output_path}")
            
            return {
                "success": True,
                "output_path": output_path,
                "seed": used_seed,
                "prompt": prompt,
                "guidance_scale": guidance_scale,
                "steps": num_inference_steps
            }
            
        except Exception as e:
            logger.error(f"Error editing image: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def batch_edit(
        self,
        image_paths: list[str],
        prompts: list[str],
        **kwargs
    ) -> list[Dict[str, Any]]:
        """
        Edit nhiều ảnh với nhiều prompts khác nhau
        
        Args:
            image_paths: List các đường dẫn ảnh
            prompts: List các prompts tương ứng
            **kwargs: Các tham số khác cho edit_image
            
        Returns:
            List các kết quả
        """
        if len(image_paths) != len(prompts):
            raise ValueError("Number of images must match number of prompts")
        
        results = []
        for image_path, prompt in zip(image_paths, prompts):
            result = await self.edit_image(image_path, prompt, **kwargs)
            results.append(result)
        
        return results
    
    async def quick_color_change(
        self,
        image_path: str,
        target_object: str,
        new_color: str
    ) -> Dict[str, Any]:
        """
        Helper method để đổi màu nhanh
        
        Args:
            image_path: Đường dẫn ảnh
            target_object: Đối tượng cần đổi màu (ví dụ: "the car", "her dress")
            new_color: Màu mới (ví dụ: "red", "light blue")
        """
        prompt = f"Change the color of {target_object} to {new_color}"
        return await self.edit_image(image_path, prompt)
    
    async def style_transfer(
        self,
        image_path: str,
        style: str
    ) -> Dict[str, Any]:
        """
        Áp dụng style cho ảnh
        
        Args:
            image_path: Đường dẫn ảnh
            style: Style mong muốn (ví dụ: "oil painting", "watercolor", "cartoon")
        """
        prompt = f"Transform this image into {style} style"
        return await self.edit_image(image_path, prompt, guidance_scale=1.5)


# Singleton instance
qwen_fast_edit_agent = QwenFastEditAgent()
