#!/usr/bin/env python3
"""Command-line interface for Deep Vision image editing."""

import argparse
import sys
import logging
from pathlib import Path

from deep_vision import ImageEditor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Deep Vision - Image editing with AI based on text prompts"
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Path to input image"
    )
    
    parser.add_argument(
        "prompt",
        type=str,
        help="Text description of desired edit"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output.png",
        help="Path to save edited image (default: output.png)"
    )
    
    parser.add_argument(
        "-n", "--negative-prompt",
        type=str,
        default=None,
        help="Negative prompt (things to avoid)"
    )
    
    parser.add_argument(
        "-s", "--strength",
        type=float,
        default=0.75,
        help="Edit strength (0.0 to 1.0, default: 0.75)"
    )
    
    parser.add_argument(
        "-g", "--guidance-scale",
        type=float,
        default=7.5,
        help="Guidance scale (default: 7.5)"
    )
    
    parser.add_argument(
        "--steps",
        type=int,
        default=50,
        help="Number of inference steps (default: 50)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "cpu", "auto"],
        default="auto",
        help="Device to use (default: auto)"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["general", "remove", "sharpen", "add", "beautify"],
        default="general",
        help="Editing mode (default: general)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input).exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)
    
    # Initialize editor
    device = None if args.device == "auto" else args.device
    editor = ImageEditor(device=device)
    
    try:
        # Edit image based on mode
        if args.mode == "remove":
            logger.info(f"Removing object: {args.prompt}")
            result = editor.remove_object(
                image=args.input,
                object_description=args.prompt,
                negative_prompt=args.negative_prompt,
                guidance_scale=args.guidance_scale,
                num_inference_steps=args.steps,
                seed=args.seed,
            )
        elif args.mode == "sharpen":
            logger.info("Sharpening image")
            result = editor.sharpen_image(
                image=args.input,
                intensity=args.prompt if args.prompt in ["low", "medium", "high"] else "medium",
                negative_prompt=args.negative_prompt,
                guidance_scale=args.guidance_scale,
                num_inference_steps=args.steps,
                seed=args.seed,
            )
        elif args.mode == "add":
            logger.info(f"Adding object: {args.prompt}")
            result = editor.add_object(
                image=args.input,
                object_description=args.prompt,
                negative_prompt=args.negative_prompt,
                guidance_scale=args.guidance_scale,
                num_inference_steps=args.steps,
                seed=args.seed,
            )
        elif args.mode == "beautify":
            logger.info("Beautifying image")
            result = editor.beautify(
                image=args.input,
                negative_prompt=args.negative_prompt,
                guidance_scale=args.guidance_scale,
                num_inference_steps=args.steps,
                seed=args.seed,
            )
        else:  # general mode
            logger.info(f"Editing with prompt: {args.prompt}")
            result = editor.edit_image(
                image=args.input,
                prompt=args.prompt,
                negative_prompt=args.negative_prompt,
                strength=args.strength,
                guidance_scale=args.guidance_scale,
                num_inference_steps=args.steps,
                seed=args.seed,
            )
        
        # Save result
        result.save(args.output)
        logger.info(f"Saved edited image to: {args.output}")
        
    except Exception as e:
        logger.error(f"Error during image editing: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
