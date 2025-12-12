"""
Qwen LoRA Fusion Agent - Multiple image editing with LoRA style fusion
Sử dụng prithivMLmods/Qwen-Image-Edit-2509-LoRAs-Fast-Fusion
"""
from gradio_client import Client, handle_file
from pathlib import Path
from typing import Optional, Dict, Any, List, Literal
from loguru import logger
import asyncio
from functools import partial
import os


LoRAAdapter = Literal[
    "Super-Fusion",
    "AI-Film-Gen",
    "HighFashion-Fusion",
    "StyAlta",
    "Holo-Neon",
    "Candy-Flash",
    "Super-Realism",
    "Neon-Anime"
]


class QwenLoRAFusionAgent:
    """
    Agent cho multiple image editing với LoRA style fusion
    Phù hợp cho: style transfer, object replacement, fashion design, creative edits
    """
    
    LORA_ADAPTERS = {
        "Super-Fusion": "Versatile fusion style for general editing",
        "AI-Film-Gen": "Cinematic film-like effects",
        "HighFashion-Fusion": "Fashion and style focused",
        "StyAlta": "Artistic style transformation",
        "Holo-Neon": "Holographic and neon effects",
        "Candy-Flash": "Vibrant candy-like colors",
        "Super-Realism": "Photorealistic enhancement",
        "Neon-Anime": "Anime style with neon accents"
    }
    
    def __init__(self):
        """Initialize Qwen LoRA Fusion client"""
        self._client = None
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        logger.info("Initialized Qwen LoRA Fusion Agent")
    
    def _get_client(self):
        """Get or create Gradio client (lazy loading)"""
        if self._client is None:
            logger.info("Connecting to Qwen-LoRA-Fusion Space...")
            self._client = Client(
                "prithivMLmods/Qwen-Image-Edit-2509-LoRAs-Fast-Fusion",
                hf_token=self.hf_token
            )
            logger.success("Connected to Qwen-LoRA-Fusion Space")
        return self._client
    
    async def edit_with_fusion(
        self,
        image_1: str,
        image_2: str,
        prompt: str,
        lora_adapter: LoRAAdapter = "Super-Fusion",
        seed: int = 0,
        randomize_seed: bool = True,
        guidance_scale: float = 1.0,
        steps: int = 4
    ) -> Dict[str, Any]:
        """
        Edit 2 images với LoRA style fusion
        
        Args:
            image_1: Đường dẫn ảnh 1 (reference/style source)
            image_2: Đường dẫn ảnh 2 (target to edit)
            prompt: Mô tả chỉnh sửa (ví dụ: "Replace her glasses with the new glasses from image 1")
            lora_adapter: LoRA style adapter
            seed: Random seed
            randomize_seed: Tự động random seed
            guidance_scale: Độ mạnh (0.5-2.0, default 1.0)
            steps: Số bước inference (4-12, default 4 cho fast)
            
        Returns:
            Dict chứa output_path và metadata
        """
        try:
            logger.info(f"Fusion editing with LoRA: {lora_adapter}")
            logger.info(f"Image 1: {image_1}")
            logger.info(f"Image 2: {image_2}")
            logger.info(f"Prompt: {prompt}")
            
            # Validate images
            if not Path(image_1).exists():
                raise FileNotFoundError(f"Image 1 not found: {image_1}")
            if not Path(image_2).exists():
                raise FileNotFoundError(f"Image 2 not found: {image_2}")
            
            # Validate LoRA adapter
            if lora_adapter not in self.LORA_ADAPTERS:
                logger.warning(f"Unknown LoRA adapter: {lora_adapter}, using Super-Fusion")
                lora_adapter = "Super-Fusion"
            
            # Run prediction
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                partial(
                    self._get_client().predict,
                    image_1=handle_file(image_1),
                    image_2=handle_file(image_2),
                    prompt=prompt,
                    lora_adapter=lora_adapter,
                    seed=seed,
                    randomize_seed=randomize_seed,
                    guidance_scale=guidance_scale,
                    steps=steps,
                    api_name="/infer"
                )
            )
            
            # Result is tuple: (image_path, seed_used)
            output_path, used_seed = result
            
            logger.success(f"Fusion edit completed: {output_path}")
            
            return {
                "success": True,
                "output_path": output_path,
                "seed": used_seed,
                "prompt": prompt,
                "lora_adapter": lora_adapter,
                "guidance_scale": guidance_scale,
                "steps": steps
            }
            
        except Exception as e:
            logger.error(f"Error in fusion edit: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def replace_object(
        self,
        source_image: str,
        target_image: str,
        object_name: str,
        lora_style: LoRAAdapter = "Super-Fusion"
    ) -> Dict[str, Any]:
        """
        Replace object từ source vào target
        
        Args:
            source_image: Ảnh chứa object cần lấy
            target_image: Ảnh đích cần thay thế
            object_name: Tên object (ví dụ: "glasses", "hat", "dress")
            lora_style: Style LoRA
        """
        prompt = f"Replace the {object_name} in image 2 with the {object_name} from image 1"
        return await self.edit_with_fusion(
            source_image,
            target_image,
            prompt,
            lora_adapter=lora_style
        )
    
    async def style_fusion(
        self,
        style_reference: str,
        target_image: str,
        lora_adapter: LoRAAdapter = "StyAlta"
    ) -> Dict[str, Any]:
        """
        Apply style từ reference image lên target
        
        Args:
            style_reference: Ảnh reference style
            target_image: Ảnh cần apply style
            lora_adapter: LoRA style (StyAlta, AI-Film-Gen, etc.)
        """
        prompt = "Apply the artistic style from image 1 to image 2 while preserving the content"
        return await self.edit_with_fusion(
            style_reference,
            target_image,
            prompt,
            lora_adapter=lora_adapter,
            guidance_scale=1.2
        )
    
    async def fashion_transfer(
        self,
        clothing_reference: str,
        person_image: str
    ) -> Dict[str, Any]:
        """
        Transfer clothing/fashion từ reference lên person
        
        Args:
            clothing_reference: Ảnh chứa trang phục reference
            person_image: Ảnh người cần thay trang phục
        """
        prompt = "Transfer the clothing and fashion style from image 1 to the person in image 2"
        return await self.edit_with_fusion(
            clothing_reference,
            person_image,
            prompt,
            lora_adapter="HighFashion-Fusion",
            guidance_scale=1.3,
            steps=6
        )
    
    async def cinematic_edit(
        self,
        reference_scene: str,
        target_image: str
    ) -> Dict[str, Any]:
        """
        Apply cinematic effects
        
        Args:
            reference_scene: Scene reference cho lighting/mood
            target_image: Ảnh cần edit
        """
        prompt = "Apply the cinematic lighting and mood from image 1 to image 2"
        return await self.edit_with_fusion(
            reference_scene,
            target_image,
            prompt,
            lora_adapter="AI-Film-Gen",
            guidance_scale=1.4
        )
    
    def list_lora_adapters(self) -> Dict[str, str]:
        """Get danh sách tất cả LoRA adapters"""
        return self.LORA_ADAPTERS


# Singleton instance
qwen_lora_fusion_agent = QwenLoRAFusionAgent()
