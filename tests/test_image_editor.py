"""Unit tests for ImageEditor class."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import numpy as np
import tempfile
import os

from deep_vision import ImageEditor


class TestImageEditor(unittest.TestCase):
    """Test cases for ImageEditor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test image
        self.test_image = Image.new('RGB', (100, 100), color='red')
        
        # Create a temporary file
        self.temp_file = tempfile.NamedTemporaryFile(
            suffix='.jpg',
            delete=False
        )
        self.test_image.save(self.temp_file.name)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_initialization_cpu(self):
        """Test ImageEditor initialization with CPU."""
        editor = ImageEditor(device="cpu")
        self.assertEqual(editor.device, "cpu")
        self.assertIsNotNone(editor.prompt_processor)
        self.assertIsNotNone(editor.image_processor)
    
    def test_initialization_auto(self):
        """Test ImageEditor initialization with auto device selection."""
        editor = ImageEditor()
        self.assertIn(editor.device, ["cuda", "cpu"])
    
    @patch('deep_vision.image_editor.PromptProcessor')
    def test_edit_image_with_pil_image(self, mock_processor_class):
        """Test edit_image with PIL Image input."""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.process.return_value = self.test_image
        mock_processor_class.return_value = mock_processor
        
        editor = ImageEditor(device="cpu")
        result = editor.edit_image(
            image=self.test_image,
            prompt="test prompt"
        )
        
        self.assertIsInstance(result, Image.Image)
        mock_processor.process.assert_called_once()
    
    @patch('deep_vision.image_editor.PromptProcessor')
    def test_edit_image_with_file_path(self, mock_processor_class):
        """Test edit_image with file path input."""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.process.return_value = self.test_image
        mock_processor_class.return_value = mock_processor
        
        editor = ImageEditor(device="cpu")
        result = editor.edit_image(
            image=self.temp_file.name,
            prompt="test prompt"
        )
        
        self.assertIsInstance(result, Image.Image)
    
    @patch('deep_vision.image_editor.PromptProcessor')
    def test_edit_image_with_numpy_array(self, mock_processor_class):
        """Test edit_image with numpy array input."""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.process.return_value = self.test_image
        mock_processor_class.return_value = mock_processor
        
        editor = ImageEditor(device="cpu")
        img_array = np.array(self.test_image)
        result = editor.edit_image(
            image=img_array,
            prompt="test prompt"
        )
        
        self.assertIsInstance(result, Image.Image)
    
    def test_edit_image_invalid_input(self):
        """Test edit_image with invalid input type."""
        editor = ImageEditor(device="cpu")
        
        with self.assertRaises(ValueError):
            editor.edit_image(
                image=12345,  # Invalid type
                prompt="test prompt"
            )
    
    @patch('deep_vision.image_editor.PromptProcessor')
    def test_remove_object(self, mock_processor_class):
        """Test remove_object method."""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.process.return_value = self.test_image
        mock_processor_class.return_value = mock_processor
        
        editor = ImageEditor(device="cpu")
        result = editor.remove_object(
            image=self.test_image,
            object_description="a person"
        )
        
        self.assertIsInstance(result, Image.Image)
        # Check that the prompt contains removal keywords
        call_args = mock_processor.process.call_args
        self.assertIn("remove", call_args[1]["prompt"].lower())
    
    @patch('deep_vision.image_editor.PromptProcessor')
    def test_sharpen_image(self, mock_processor_class):
        """Test sharpen_image method."""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.process.return_value = self.test_image
        mock_processor_class.return_value = mock_processor
        
        editor = ImageEditor(device="cpu")
        result = editor.sharpen_image(
            image=self.test_image,
            intensity="high"
        )
        
        self.assertIsInstance(result, Image.Image)
        # Check that the prompt contains sharpening keywords
        call_args = mock_processor.process.call_args
        prompt = call_args[1]["prompt"].lower()
        self.assertTrue(any(word in prompt for word in ["sharp", "detail", "crisp"]))
    
    @patch('deep_vision.image_editor.PromptProcessor')
    def test_add_object(self, mock_processor_class):
        """Test add_object method."""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.process.return_value = self.test_image
        mock_processor_class.return_value = mock_processor
        
        editor = ImageEditor(device="cpu")
        result = editor.add_object(
            image=self.test_image,
            object_description="a tree",
            location="on the left"
        )
        
        self.assertIsInstance(result, Image.Image)
        # Check that the prompt contains add keywords
        call_args = mock_processor.process.call_args
        prompt = call_args[1]["prompt"].lower()
        self.assertIn("add", prompt)
        self.assertIn("tree", prompt)
        self.assertIn("on the left", prompt)
    
    @patch('deep_vision.image_editor.PromptProcessor')
    def test_beautify(self, mock_processor_class):
        """Test beautify method."""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.process.return_value = self.test_image
        mock_processor_class.return_value = mock_processor
        
        editor = ImageEditor(device="cpu")
        result = editor.beautify(
            image=self.test_image,
            features=["skin", "eyes"]
        )
        
        self.assertIsInstance(result, Image.Image)
        # Check that the prompt contains beautify keywords
        call_args = mock_processor.process.call_args
        prompt = call_args[1]["prompt"].lower()
        self.assertIn("beautify", prompt)
        self.assertIn("skin", prompt)
        self.assertIn("eyes", prompt)
    
    @patch('deep_vision.image_editor.PromptProcessor')
    def test_edit_with_parameters(self, mock_processor_class):
        """Test edit_image with various parameters."""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.process.return_value = self.test_image
        mock_processor_class.return_value = mock_processor
        
        editor = ImageEditor(device="cpu")
        result = editor.edit_image(
            image=self.test_image,
            prompt="test prompt",
            negative_prompt="bad quality",
            strength=0.8,
            guidance_scale=8.0,
            num_inference_steps=75,
            seed=42
        )
        
        self.assertIsInstance(result, Image.Image)
        call_args = mock_processor.process.call_args[1]
        self.assertEqual(call_args["negative_prompt"], "bad quality")
        self.assertEqual(call_args["guidance_scale"], 8.0)
        self.assertEqual(call_args["num_inference_steps"], 75)
        self.assertEqual(call_args["seed"], 42)


if __name__ == '__main__':
    unittest.main()
