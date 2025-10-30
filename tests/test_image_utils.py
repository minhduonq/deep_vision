"""Unit tests for image utilities."""

import unittest
import numpy as np
from PIL import Image

from deep_vision.utils.image_utils import ImageProcessor


class TestImageProcessor(unittest.TestCase):
    """Test cases for ImageProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_image = Image.new('RGB', (100, 100), color='red')
        self.processor = ImageProcessor()
    
    def test_resize_image_no_change(self):
        """Test resize when image is smaller than max_size."""
        result = self.processor.resize_image(self.test_image, max_size=512)
        self.assertEqual(result.size, self.test_image.size)
    
    def test_resize_image_downscale(self):
        """Test resize when image is larger than max_size."""
        large_image = Image.new('RGB', (1024, 768), color='blue')
        result = self.processor.resize_image(large_image, max_size=512)
        
        self.assertLessEqual(max(result.size), 512)
        self.assertGreater(result.size[0], 0)
        self.assertGreater(result.size[1], 0)
    
    def test_resize_image_keep_aspect_ratio(self):
        """Test that aspect ratio is preserved."""
        large_image = Image.new('RGB', (1000, 500), color='green')
        result = self.processor.resize_image(large_image, max_size=512, keep_aspect_ratio=True)
        
        # Check aspect ratio is preserved
        original_ratio = large_image.size[0] / large_image.size[1]
        result_ratio = result.size[0] / result.size[1]
        self.assertAlmostEqual(original_ratio, result_ratio, places=1)
    
    def test_resize_image_no_aspect_ratio(self):
        """Test resize without keeping aspect ratio."""
        large_image = Image.new('RGB', (1000, 500), color='yellow')
        result = self.processor.resize_image(large_image, max_size=512, keep_aspect_ratio=False)
        
        self.assertEqual(result.size, (512, 512))
    
    def test_sharpen_image_cv(self):
        """Test image sharpening."""
        result = self.processor.sharpen_image_cv(self.test_image, intensity=1.0)
        
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, self.test_image.size)
    
    def test_sharpen_image_cv_different_intensities(self):
        """Test sharpening with different intensities."""
        intensities = [0.5, 1.0, 1.5]
        
        for intensity in intensities:
            result = self.processor.sharpen_image_cv(self.test_image, intensity=intensity)
            self.assertIsInstance(result, Image.Image)
            self.assertEqual(result.size, self.test_image.size)
    
    def test_enhance_details(self):
        """Test detail enhancement."""
        result = self.processor.enhance_details(self.test_image)
        
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, self.test_image.size)
    
    def test_create_mask_default(self):
        """Test mask creation with default center region."""
        mask = self.processor.create_mask((100, 100))
        
        self.assertIsInstance(mask, Image.Image)
        self.assertEqual(mask.size, (100, 100))
        
        # Check that mask has white pixels in center
        mask_array = np.array(mask)
        self.assertTrue(np.any(mask_array == 255))
    
    def test_create_mask_custom_region(self):
        """Test mask creation with custom region."""
        mask_region = (20, 20, 40, 40)  # x, y, width, height
        mask = self.processor.create_mask((100, 100), mask_region=mask_region)
        
        self.assertIsInstance(mask, Image.Image)
        self.assertEqual(mask.size, (100, 100))
        
        # Check that mask has white pixels in specified region
        mask_array = np.array(mask)
        region_mask = mask_array[20:60, 20:60]
        self.assertTrue(np.all(region_mask == 255))
    
    def test_blend_images_equal_size(self):
        """Test blending two images of equal size."""
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')
        
        result = self.processor.blend_images(img1, img2, alpha=0.5)
        
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, img1.size)
    
    def test_blend_images_different_size(self):
        """Test blending images of different sizes."""
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (200, 150), color='blue')
        
        result = self.processor.blend_images(img1, img2, alpha=0.5)
        
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, img1.size)
    
    def test_blend_images_different_alphas(self):
        """Test blending with different alpha values."""
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')
        
        alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for alpha in alphas:
            result = self.processor.blend_images(img1, img2, alpha=alpha)
            self.assertIsInstance(result, Image.Image)
            self.assertEqual(result.size, img1.size)


if __name__ == '__main__':
    unittest.main()
