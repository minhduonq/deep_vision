"""Image processing utilities."""

import numpy as np
from PIL import Image
from typing import Tuple, Optional

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


class ImageProcessor:
    """Utility class for image preprocessing and postprocessing."""
    
    @staticmethod
    def resize_image(
        image: Image.Image,
        max_size: int = 512,
        keep_aspect_ratio: bool = True
    ) -> Image.Image:
        """
        Resize image to fit within max_size.
        
        Args:
            image: Input PIL Image
            max_size: Maximum dimension size
            keep_aspect_ratio: Whether to maintain aspect ratio
            
        Returns:
            Resized PIL Image
        """
        if keep_aspect_ratio:
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                return image.resize(new_size, Image.Resampling.LANCZOS)
        else:
            return image.resize((max_size, max_size), Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def sharpen_image_cv(image: Image.Image, intensity: float = 1.0) -> Image.Image:
        """
        Sharpen image using OpenCV (or PIL if OpenCV not available).
        
        Args:
            image: Input PIL Image
            intensity: Sharpening intensity (0.0 to 2.0)
            
        Returns:
            Sharpened PIL Image
        """
        if not HAS_CV2:
            # Fallback to PIL sharpening
            from PIL import ImageFilter, ImageEnhance
            sharpened = image.filter(ImageFilter.SHARPEN)
            enhancer = ImageEnhance.Sharpness(sharpened)
            return enhancer.enhance(1.0 + intensity)
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(img_array, (0, 0), 3)
        
        # Sharpen using unsharp mask
        sharpened = cv2.addWeighted(img_array, 1.0 + intensity, blurred, -intensity, 0)
        
        return Image.fromarray(sharpened)
    
    @staticmethod
    def enhance_details(image: Image.Image) -> Image.Image:
        """
        Enhance image details using CLAHE (or PIL if OpenCV not available).
        
        Args:
            image: Input PIL Image
            
        Returns:
            Enhanced PIL Image
        """
        if not HAS_CV2:
            # Fallback to PIL enhancement
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            enhanced = enhancer.enhance(1.2)
            sharpener = ImageEnhance.Sharpness(enhanced)
            return sharpener.enhance(1.3)
        
        img_array = np.array(image)
        
        # Convert to LAB color space
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        return Image.fromarray(enhanced)
    
    @staticmethod
    def create_mask(
        image_size: Tuple[int, int],
        mask_region: Optional[Tuple[int, int, int, int]] = None
    ) -> Image.Image:
        """
        Create a binary mask for inpainting.
        
        Args:
            image_size: (width, height) of the image
            mask_region: (x, y, width, height) of region to mask, or None for center
            
        Returns:
            Binary mask as PIL Image
        """
        mask = np.zeros((image_size[1], image_size[0]), dtype=np.uint8)
        
        if mask_region is None:
            # Default to center region
            center_x, center_y = image_size[0] // 2, image_size[1] // 2
            size = min(image_size) // 4
            x1, y1 = center_x - size // 2, center_y - size // 2
            x2, y2 = center_x + size // 2, center_y + size // 2
        else:
            x1, y1, w, h = mask_region
            x2, y2 = x1 + w, y1 + h
        
        mask[y1:y2, x1:x2] = 255
        
        return Image.fromarray(mask)
    
    @staticmethod
    def blend_images(
        img1: Image.Image,
        img2: Image.Image,
        alpha: float = 0.5
    ) -> Image.Image:
        """
        Blend two images together.
        
        Args:
            img1: First PIL Image
            img2: Second PIL Image
            alpha: Blending factor (0.0 to 1.0)
            
        Returns:
            Blended PIL Image
        """
        # Ensure same size
        if img1.size != img2.size:
            img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
        
        # Convert to arrays
        arr1 = np.array(img1, dtype=np.float32)
        arr2 = np.array(img2, dtype=np.float32)
        
        # Blend
        blended = (alpha * arr1 + (1 - alpha) * arr2).astype(np.uint8)
        
        return Image.fromarray(blended)
