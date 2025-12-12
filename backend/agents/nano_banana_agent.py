"""
Nano Banana Agent - Sử dụng Google Nano Banana từ Replicate cho các tác vụ chỉnh sửa ảnh
API Documentation: https://replicate.com/google/nano-banana
"""
import replicate
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from loguru import logger
import asyncio
from functools import partial
import os
import io
from PIL import Image

class NanoBananaAgent:
    """
    Agent sử dụng Google Nano Banana từ Replicate cho image editing tasks
    Hỗ trợ chỉnh sửa ảnh với prompt, tương tự như Qwen Fast Edit
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Args:
            api_token: Replicate API token (hoặc set qua env var REPLICATE_API_TOKEN)
        """
        if api_token:
            os.environ["REPLICATE_API_TOKEN"] = api_token
        
        self.model_name = "google/nano-banana"
        self.max_images = 10  # API supports multiple input images
        logger.info("Initialized Nano Banana Agent")
    
    async def edit_image(
        self,
        image_path: Union[str, List[str]],
        prompt: str,
        aspect_ratio: str = "match_input_image",
        output_format: str = "jpg",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chỉnh sửa ảnh theo prompt sử dụng Google Nano Banana
        Hỗ trợ 1 hoặc nhiều ảnh input (tối đa 10 ảnh)
        
        Args:
            image_path: Đường dẫn ảnh input (str) hoặc list đường dẫn
            prompt: Mô tả cách chỉnh sửa (ví dụ: "Make the sheets in the style of the logo. Make the scene natural.")
            aspect_ratio: Tỷ lệ khung hình - "match_input_image", "1:1", "16:9", "9:16", "4:3", "3:4", etc.
            output_format: "jpg" hoặc "png"
            output_dir: Thư mục lưu kết quả (nếu None, trả về URL)
            
        Returns:
            Dict chứa đường dẫn ảnh kết quả và metadata
        """
        try:
            # Handle single or multiple images
            image_paths = [image_path] if isinstance(image_path, str) else image_path
            
            if len(image_paths) > self.max_images:
                logger.warning(f"Too many images ({len(image_paths)}), limiting to {self.max_images}")
                image_paths = image_paths[:self.max_images]
            
            logger.info(f"Editing {len(image_paths)} image(s) with Nano Banana")
            logger.info(f"Prompt: {prompt}")
            
            # Prepare input following the API documentation format
            # Convert local file paths to file handles
            image_inputs = []
            for img_path in image_paths:
                if os.path.isfile(img_path):
                    # Open file for Replicate API
                    image_inputs.append(open(img_path, "rb"))
                else:
                    # If it's already a URL, use directly
                    image_inputs.append(img_path)
            
            input_dict = {
                "prompt": prompt,
                "image_input": image_inputs,
                "aspect_ratio": aspect_ratio,
                "output_format": output_format
            }
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(
                None,
                partial(
                    replicate.run,
                    self.model_name,
                    input=input_dict
                )
            )
            
            # Close file handles if opened
            for img_input in image_inputs:
                if hasattr(img_input, 'close'):
                    img_input.close()
            
            logger.success(f"Image(s) edited successfully")
            
            # Handle output - can be FileOutput object or URL
            output_path = None
            if output_dir:
                # Save to disk if output_dir is specified
                output_dir_path = Path(output_dir)
                output_dir_path.mkdir(parents=True, exist_ok=True)
                
                output_file = output_dir_path / f"nano_banana_output.{output_format}"
                
                # Write output to file
                with open(output_file, "wb") as f:
                    if hasattr(output, 'read'):
                        f.write(output.read())
                    else:
                        # If it's a URL, download it
                        import requests
                        response = requests.get(str(output))
                        f.write(response.content)
                
                output_path = str(output_file)
                logger.info(f"Saved output to: {output_path}")
            else:
                # Return URL
                output_path = output.url() if hasattr(output, 'url') else str(output)
            
            return {
                "success": True,
                "output_path": output_path,
                "num_images": len(image_paths),
                "metadata": {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "output_format": output_format,
                    "model": "Google Nano Banana",
                    "model_version": self.model_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error editing image with Nano Banana: {str(e)}")
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
        strength: str = "medium",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Làm sắc nét ảnh bị mờ (hỗ trợ nhiều ảnh)
        
        Args:
            image_path: Đường dẫn ảnh hoặc list đường dẫn
            strength: "light", "medium", "strong"
            output_dir: Thư mục lưu kết quả
        """
        prompts = {
            "light": "Slightly sharpen this image, enhance clarity and details",
            "medium": "Remove blur and make this image sharp and clear, enhance all details",
            "strong": "Significantly enhance sharpness, remove all blur, maximize clarity and detail"
        }
        
        prompt = prompts.get(strength, prompts["medium"])
        
        return await self.edit_image(
            image_path, 
            prompt,
            output_dir=output_dir
        )
    
    async def remove_object(
        self,
        image_path: Union[str, List[str]],
        object_description: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Xóa object khỏi ảnh (hỗ trợ nhiều ảnh)
        
        Args:
            image_path: Đường dẫn ảnh hoặc list đường dẫn
            object_description: Mô tả object cần xóa
            output_dir: Thư mục lưu kết quả
        """
        prompt = f"Remove {object_description} from this image, fill the area naturally and seamlessly"
        
        return await self.edit_image(
            image_path, 
            prompt,
            output_dir=output_dir
        )
    
    async def beauty_enhance(
        self,
        image_path: Union[str, List[str]],
        level: str = "natural",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Làm đẹp khuôn mặt (hỗ trợ nhiều ảnh)
        
        Args:
            image_path: Đường dẫn ảnh hoặc list đường dẫn
            level: "subtle", "natural", "strong"
            output_dir: Thư mục lưu kết quả
        """
        prompts = {
            "subtle": "Subtly enhance facial features, smooth skin tone naturally, maintain authenticity",
            "natural": "Enhance facial beauty naturally, smooth skin, brighten eyes, perfect lighting",
            "strong": "Professional beauty enhancement, flawless skin, perfect features, magazine quality"
        }
        
        prompt = prompts.get(level, prompts["natural"])
        
        return await self.edit_image(
            image_path, 
            prompt,
            output_dir=output_dir
        )
    
    async def style_transfer(
        self,
        image_path: Union[str, List[str]],
        style: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chuyển đổi style ảnh (hỗ trợ nhiều ảnh)
        
        Args:
            image_path: Đường dẫn ảnh hoặc list đường dẫn
            style: Mô tả style
            output_dir: Thư mục lưu kết quả
        """
        prompt = f"Transform this image into {style} style, maintain composition and subjects"
        
        return await self.edit_image(
            image_path, 
            prompt,
            output_dir=output_dir
        )
    
    async def upscale_and_enhance(
        self,
        image_path: Union[str, List[str]],
        enhancement_level: str = "medium",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upscale và enhance ảnh (hỗ trợ nhiều ảnh)
        
        Args:
            image_path: Đường dẫn ảnh hoặc list đường dẫn
            enhancement_level: "light", "medium", "strong"
            output_dir: Thư mục lưu kết quả
        """
        prompts = {
            "light": "Upscale this image, slightly enhance quality and details",
            "medium": "Upscale this image, enhance quality, sharpen details, improve colors",
            "strong": "Upscale this image to highest quality, maximize sharpness and details, perfect colors"
        }
        
        prompt = prompts.get(enhancement_level, prompts["medium"])
        
        return await self.edit_image(
            image_path, 
            prompt,
            output_format="png",  # Use PNG for better quality in upscaling
            output_dir=output_dir
        )
    
    async def process_edit_request(
        self,
        image_path: str,
        prompt: str,
        output_dir: str,
        aspect_ratio: str = "match_input_image",
        output_format: str = "jpg"
    ) -> Dict[str, Any]:
        """
        Method tích hợp với orchestrator để xử lý yêu cầu chỉnh sửa ảnh
        Interface tương tự Qwen Edit Agent để dễ dàng thay thế/kết hợp
        
        Args:
            image_path: Đường dẫn ảnh input
            prompt: Mô tả yêu cầu chỉnh sửa
            output_dir: Thư mục lưu kết quả
            aspect_ratio: Tỷ lệ khung hình
            output_format: Định dạng output
            
        Returns:
            Dict chứa kết quả xử lý
        """
        logger.info(f"[Nano Banana] Processing edit request")
        logger.info(f"Image: {image_path}")
        logger.info(f"Prompt: {prompt}")
        
        result = await self.edit_image(
            image_path=image_path,
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            output_format=output_format,
            output_dir=output_dir
        )
        
        if result["success"]:
            logger.success(f"[Nano Banana] Edit completed successfully")
        else:
            logger.error(f"[Nano Banana] Edit failed: {result.get('error')}")
        
        return result


# Singleton instance
nano_banana_agent = NanoBananaAgent()