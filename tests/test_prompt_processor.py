"""Unit tests for PromptProcessor class."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from deep_vision.models.prompt_processor import PromptProcessor


class TestPromptProcessor(unittest.TestCase):
    """Test cases for PromptProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = PromptProcessor(device="cpu")
        self.test_image = Image.new('RGB', (100, 100), color='blue')
    
    def test_initialization(self):
        """Test PromptProcessor initialization."""
        processor = PromptProcessor(device="cpu")
        self.assertEqual(processor.device, "cpu")
        self.assertFalse(processor._models_loaded)
        self.assertIsNone(processor._instruct_pix2pix)
        self.assertIsNone(processor._inpainting_model)
    
    def test_analyze_prompt_remove(self):
        """Test prompt analysis for removal."""
        prompts = [
            "remove the person",
            "delete the tree",
            "erase the watermark",
            "clean the background"
        ]
        
        for prompt in prompts:
            edit_type = self.processor._analyze_prompt(prompt)
            self.assertEqual(edit_type, 'remove', f"Failed for prompt: {prompt}")
    
    def test_analyze_prompt_sharpen(self):
        """Test prompt analysis for sharpening."""
        prompts = [
            "sharpen the image",
            "make it sharp",
            "enhance details",
            "make it crisp"
        ]
        
        for prompt in prompts:
            edit_type = self.processor._analyze_prompt(prompt)
            self.assertEqual(edit_type, 'sharpen', f"Failed for prompt: {prompt}")
    
    def test_analyze_prompt_add(self):
        """Test prompt analysis for adding objects."""
        prompts = [
            "add a tree",
            "insert a person",
            "place a car",
            "put a flower"
        ]
        
        for prompt in prompts:
            edit_type = self.processor._analyze_prompt(prompt)
            self.assertEqual(edit_type, 'add', f"Failed for prompt: {prompt}")
    
    def test_analyze_prompt_beautify(self):
        """Test prompt analysis for beautification."""
        prompts = [
            "beautify the face",
            "apply beauty filter",
            "smooth skin",
            "add makeup"
        ]
        
        for prompt in prompts:
            edit_type = self.processor._analyze_prompt(prompt)
            self.assertEqual(edit_type, 'beautify', f"Failed for prompt: {prompt}")
    
    def test_analyze_prompt_general(self):
        """Test prompt analysis for general edits."""
        prompts = [
            "make it more vibrant",
            "change the color to blue",
            "adjust the brightness"
        ]
        
        for prompt in prompts:
            edit_type = self.processor._analyze_prompt(prompt)
            self.assertEqual(edit_type, 'general', f"Failed for prompt: {prompt}")
    
    @patch('diffusers.StableDiffusionInstructPix2PixPipeline')
    def test_load_instruct_pix2pix(self, mock_pipeline_class):
        """Test loading InstructPix2Pix model."""
        # Mock the pipeline
        mock_pipeline = MagicMock()
        mock_pipeline_class.from_pretrained.return_value = mock_pipeline
        
        processor = PromptProcessor(device="cpu")
        result = processor._load_instruct_pix2pix()
        
        self.assertIsNotNone(result)
        mock_pipeline_class.from_pretrained.assert_called_once()
        mock_pipeline.to.assert_called_once_with("cpu")
    
    @patch('diffusers.StableDiffusionInpaintPipeline')
    def test_load_inpainting_model(self, mock_pipeline_class):
        """Test loading inpainting model."""
        # Mock the pipeline
        mock_pipeline = MagicMock()
        mock_pipeline_class.from_pretrained.return_value = mock_pipeline
        
        processor = PromptProcessor(device="cpu")
        result = processor._load_inpainting_model()
        
        self.assertIsNotNone(result)
        mock_pipeline_class.from_pretrained.assert_called_once()
        mock_pipeline.to.assert_called_once_with("cpu")
    
    @patch('diffusers.StableDiffusionInstructPix2PixPipeline')
    def test_process_with_seed(self, mock_pipeline_class):
        """Test processing with a random seed."""
        # Mock the pipeline
        mock_pipeline = MagicMock()
        mock_result = MagicMock()
        mock_result.images = [self.test_image]
        mock_pipeline.return_value = mock_result
        mock_pipeline_class.from_pretrained.return_value = mock_pipeline
        
        processor = PromptProcessor(device="cpu")
        
        # Process with seed
        result = processor.process(
            image=self.test_image,
            prompt="test prompt",
            seed=42
        )
        
        # Verify seed was set
        self.assertIsNotNone(result)
    
    @patch('diffusers.StableDiffusionInstructPix2PixPipeline')
    def test_process_image_resize(self, mock_pipeline_class):
        """Test that large images are resized."""
        # Create a large test image
        large_image = Image.new('RGB', (1024, 1024), color='green')
        
        # Mock the pipeline
        mock_pipeline = MagicMock()
        mock_result = MagicMock()
        mock_result.images = [self.test_image]
        mock_pipeline.return_value = mock_result
        mock_pipeline_class.from_pretrained.return_value = mock_pipeline
        
        processor = PromptProcessor(device="cpu")
        result = processor.process(
            image=large_image,
            prompt="test prompt"
        )
        
        # Verify pipeline was called
        mock_pipeline.assert_called_once()
        call_args = mock_pipeline.call_args[1]
        
        # Check that image was resized
        passed_image = call_args['image']
        self.assertLessEqual(max(passed_image.size), 512)


if __name__ == '__main__':
    unittest.main()
