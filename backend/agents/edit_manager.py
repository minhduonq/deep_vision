"""
Image Edit Manager - Quản lý và fallback giữa các agent chỉnh sửa ảnh
"""
from typing import Dict, Any, Optional
from loguru import logger

from .qwen_edit_agent import qwen_edit_agent, qwen_edit_agent_fast
from .nano_banana_agent import nano_banana_agent


class ImageEditManager:
    """
    Manager để tự động fallback giữa các agent
    """
    
    def __init__(self, prefer_qwen: bool = True):
        """
        Args:
            prefer_qwen: Ưu tiên dùng Qwen trước, fallback sang Nano Banana nếu lỗi
        """
        self.prefer_qwen = prefer_qwen
        self.primary_agent = qwen_edit_agent if prefer_qwen else nano_banana_agent
        self.fallback_agent = nano_banana_agent if prefer_qwen else qwen_edit_agent
    
    async def edit_image(self, *args, **kwargs) -> Dict[str, Any]:
        """Try primary agent, fallback to secondary if fails"""
        try:
            result = await self.primary_agent.edit_image(*args, **kwargs)
            if result.get("success"):
                return result
            
            logger.warning("Primary agent failed, trying fallback...")
            return await self.fallback_agent.edit_image(*args, **kwargs)
        except Exception as e:
            logger.error(f"Primary agent error: {e}, trying fallback...")
            return await self.fallback_agent.edit_image(*args, **kwargs)
    
    async def deblur(self, *args, **kwargs) -> Dict[str, Any]:
        try:
            result = await self.primary_agent.deblur(*args, **kwargs)
            if result.get("success"):
                return result
            return await self.fallback_agent.deblur(*args, **kwargs)
        except Exception:
            return await self.fallback_agent.deblur(*args, **kwargs)
    
    async def remove_object(self, *args, **kwargs) -> Dict[str, Any]:
        try:
            result = await self.primary_agent.remove_object(*args, **kwargs)
            if result.get("success"):
                return result
            return await self.fallback_agent.remove_object(*args, **kwargs)
        except Exception:
            return await self.fallback_agent.remove_object(*args, **kwargs)
    
    async def beauty_enhance(self, *args, **kwargs) -> Dict[str, Any]:
        try:
            result = await self.primary_agent.beauty_enhance(*args, **kwargs)
            if result.get("success"):
                return result
            return await self.fallback_agent.beauty_enhance(*args, **kwargs)
        except Exception:
            return await self.fallback_agent.beauty_enhance(*args, **kwargs)
    
    async def style_transfer(self, *args, **kwargs) -> Dict[str, Any]:
        try:
            result = await self.primary_agent.style_transfer(*args, **kwargs)
            if result.get("success"):
                return result
            return await self.fallback_agent.style_transfer(*args, **kwargs)
        except Exception:
            return await self.fallback_agent.style_transfer(*args, **kwargs)
    
    async def upscale_and_enhance(self, *args, **kwargs) -> Dict[str, Any]:
        try:
            result = await self.primary_agent.upscale_and_enhance(*args, **kwargs)
            if result.get("success"):
                return result
            return await self.fallback_agent.upscale_and_enhance(*args, **kwargs)
        except Exception:
            return await self.fallback_agent.upscale_and_enhance(*args, **kwargs)


# Default manager instance
image_edit_manager = ImageEditManager(prefer_qwen=True)