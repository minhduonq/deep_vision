"""
Setup script: Download all model weights automatically
Run this to setup local models for the first time
"""

import os
from pathlib import Path
import requests
from tqdm import tqdm
from loguru import logger


# Model configurations
MODELS = {
    "nafnet_gopro": {
        "url": "https://github.com/megvii-research/NAFNet/releases/download/v1.0.0/NAFNet-GoPro-width32.pth",
        "filename": "NAFNet-GoPro-width32.pth",
        "size_mb": 16,
        "required": True
    },
    "gfpgan": {
        "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth",
        "filename": "GFPGANv1.3.pth",
        "size_mb": 348,
        "required": True
    },
    "codeformer": {
        "url": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth",
        "filename": "codeformer.pth",
        "size_mb": 376,
        "required": False
    },
    "lama": {
        "url": "https://huggingface.co/smartywu/big-lama/resolve/main/big-lama.pt?download=true",
        "filename": "big-lama.pt",
        "size_mb": 200,
        "required": True
    }
}


def download_file(url: str, output_path: Path, description: str = "Downloading"):
    """
    Download file with progress bar
    
    Args:
        url: Download URL
        output_path: Where to save file
        description: Description for progress bar
    """
    try:
        # Send request
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get total size
        total_size = int(response.headers.get('content-length', 0))
        
        # Download with progress bar
        with open(output_path, 'wb') as f:
            with tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=description,
                ncols=100
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        logger.info(f"✅ Downloaded: {output_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return False


def check_existing(filepath: Path) -> bool:
    """Check if model already exists"""
    if filepath.exists():
        size_mb = filepath.stat().st_size / (1024 * 1024)
        logger.info(f"✓ Found existing: {filepath.name} ({size_mb:.1f}MB)")
        return True
    return False


def setup_models(models_dir: Path = None, download_optional: bool = False):
    """
    Download all required model weights
    
    Args:
        models_dir: Directory to save models (default: project_root/models)
        download_optional: Whether to download optional models
    """
    # Setup paths
    if models_dir is None:
        project_root = Path(__file__).parent
        models_dir = project_root / "models"
    
    models_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("="*70)
    logger.info("🚀 Deep Vision - Model Setup")
    logger.info("="*70)
    logger.info(f"Models directory: {models_dir}")
    logger.info("")
    
    # Calculate total download size
    total_size = sum(
        model['size_mb'] 
        for model in MODELS.values() 
        if model['required'] or download_optional
    )
    logger.info(f"📦 Total download size: ~{total_size}MB")
    logger.info("")
    
    # Download each model
    downloaded = 0
    skipped = 0
    failed = 0
    
    for model_name, config in MODELS.items():
        # Skip optional models if not requested
        if not config['required'] and not download_optional:
            logger.info(f"⊘ Skipping optional model: {model_name}")
            skipped += 1
            continue
        
        # Check if already exists
        output_path = models_dir / config['filename']
        
        if check_existing(output_path):
            skipped += 1
            continue
        
        # Download
        logger.info(f"📥 Downloading {model_name} ({config['size_mb']}MB)...")
        
        success = download_file(
            url=config['url'],
            output_path=output_path,
            description=f"Downloading {config['filename']}"
        )
        
        if success:
            downloaded += 1
        else:
            failed += 1
        
        logger.info("")
    
    # Summary
    logger.info("="*70)
    logger.info("📊 Setup Summary")
    logger.info("="*70)
    logger.info(f"✅ Downloaded: {downloaded}")
    logger.info(f"⊙ Already exists: {skipped}")
    logger.info(f"❌ Failed: {failed}")
    logger.info("")
    
    if failed == 0:
        logger.info("🎉 All models ready!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Install dependencies: pip install -r requirements.txt")
        logger.info("2. Test agents: python test_agents.py")
        logger.info("3. Run backend: python backend/api/main.py")
    else:
        logger.warning("⚠️  Some models failed to download")
        logger.info("Please check your internet connection and try again")


def verify_models(models_dir: Path = None):
    """
    Verify all downloaded models
    """
    if models_dir is None:
        project_root = Path(__file__).parent
        models_dir = project_root / "models"
    
    logger.info("🔍 Verifying models...")
    logger.info("")
    
    all_ok = True
    
    for model_name, config in MODELS.items():
        if not config['required']:
            continue
        
        filepath = models_dir / config['filename']
        
        if not filepath.exists():
            logger.error(f"❌ Missing: {config['filename']}")
            all_ok = False
        else:
            size_mb = filepath.stat().st_size / (1024 * 1024)
            expected_size = config['size_mb']
            
            # Check if size matches (allow 10% variance)
            if abs(size_mb - expected_size) / expected_size > 0.1:
                logger.warning(f"⚠️  Size mismatch: {config['filename']}")
                logger.warning(f"   Expected: ~{expected_size}MB, Got: {size_mb:.1f}MB")
            else:
                logger.info(f"✅ OK: {config['filename']} ({size_mb:.1f}MB)")
    
    logger.info("")
    
    if all_ok:
        logger.info("✅ All required models are present!")
    else:
        logger.error("❌ Some models are missing. Run setup again.")
    
    return all_ok


def clean_models(models_dir: Path = None):
    """
    Remove all downloaded models
    """
    if models_dir is None:
        project_root = Path(__file__).parent
        models_dir = project_root / "models"
    
    logger.warning("🗑️  This will delete all downloaded models!")
    confirm = input("Are you sure? (y/N): ")
    
    if confirm.lower() != 'y':
        logger.info("Cancelled")
        return
    
    if not models_dir.exists():
        logger.info("Models directory doesn't exist")
        return
    
    # Delete all model files
    deleted = 0
    for model_file in models_dir.glob("*.pth"):
        model_file.unlink()
        logger.info(f"Deleted: {model_file.name}")
        deleted += 1
    
    for model_file in models_dir.glob("*.pt"):
        model_file.unlink()
        logger.info(f"Deleted: {model_file.name}")
        deleted += 1
    
    logger.info(f"✅ Deleted {deleted} model files")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup local models for Deep Vision")
    parser.add_argument(
        "--download-optional",
        action="store_true",
        help="Download optional models (CodeFormer, etc.)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify downloaded models"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete all downloaded models"
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        help="Custom models directory"
    )
    
    args = parser.parse_args()
    
    if args.clean:
        clean_models(args.models_dir)
    elif args.verify:
        verify_models(args.models_dir)
    else:
        setup_models(args.models_dir, args.download_optional)
