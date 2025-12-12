"""
Test all local model agents
Run this to verify your implementations
"""

import asyncio
from pathlib import Path
import time
from loguru import logger
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_deblur_agent():
    """Test deblur agent"""
    try:
        from backend.models.deblur_agent import deblur_agent
        
        logger.info("="*70)
        logger.info("1️⃣  Testing Deblur Agent (NAFNet-Small)")
        logger.info("="*70)
        
        # Create test image path
        test_image = Path("test_images/blurry_sample.jpg")
        
        if not test_image.exists():
            logger.warning(f"Test image not found: {test_image}")
            logger.info("Please add a blurry test image to test_images/")
            return False
        
        # Test processing
        start = time.time()
        output_path = await deblur_agent.process(test_image)
        elapsed = time.time() - start
        
        logger.info(f"✅ Deblur completed in {elapsed:.2f}s")
        logger.info(f"Output: {output_path}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        logger.info("Make sure deblur_agent.py is implemented")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def test_inpaint_agent():
    """Test inpaint agent"""
    try:
        from backend.models.inpaint_agent import inpaint_agent
        
        logger.info("\n" + "="*70)
        logger.info("2️⃣  Testing Inpaint Agent (LaMa)")
        logger.info("="*70)
        
        test_image = Path("test_images/object_sample.jpg")
        
        if not test_image.exists():
            logger.warning(f"Test image not found: {test_image}")
            return False
        
        start = time.time()
        output_path = await inpaint_agent.process(test_image)
        elapsed = time.time() - start
        
        logger.info(f"✅ Inpaint completed in {elapsed:.2f}s")
        logger.info(f"Output: {output_path}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        logger.info("💡 Hint: Implement backend/models/inpaint_agent.py")
        logger.info("📖 See: LOCAL_MODELS_TUTORIAL.md section 3")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def test_beauty_agent():
    """Test beauty enhancement agent"""
    try:
        from backend.models.beauty_agent import beauty_agent_gfpgan
        
        logger.info("\n" + "="*70)
        logger.info("3️⃣  Testing Beauty Agent (GFPGAN)")
        logger.info("="*70)
        
        test_image = Path("test_images/portrait_sample.jpg")
        
        if not test_image.exists():
            logger.warning(f"Test image not found: {test_image}")
            return False
        
        start = time.time()
        output_path = await beauty_agent_gfpgan.process(test_image)
        elapsed = time.time() - start
        
        logger.info(f"✅ Beauty enhancement completed in {elapsed:.2f}s")
        logger.info(f"Output: {output_path}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        logger.info("💡 Hint: Implement backend/models/beauty_agent.py")
        logger.info("📖 See: LOCAL_MODELS_TUTORIAL.md section 4")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def test_generation_agent():
    """Test image generation agent"""
    try:
        from backend.models.generation_agent import generation_agent
        
        logger.info("\n" + "="*70)
        logger.info("4️⃣  Testing Generation Agent (HuggingFace API)")
        logger.info("="*70)
        
        prompt = "a cute cat sitting on a table"
        
        start = time.time()
        output_path = await generation_agent.process(prompt)
        elapsed = time.time() - start
        
        logger.info(f"✅ Generation completed in {elapsed:.2f}s")
        logger.info(f"Output: {output_path}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        logger.info("💡 Hint: Implement backend/models/generation_agent.py")
        logger.info("📖 See: LOCAL_MODELS_TUTORIAL.md section 5")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def test_all():
    """Run all tests"""
    logger.info("🧪 Testing all local model agents...")
    logger.info("")
    
    # Ensure test_images directory exists
    test_images_dir = Path("test_images")
    test_images_dir.mkdir(exist_ok=True)
    
    results = {
        "Deblur": False,
        "Inpaint": False,
        "Beauty": False,
        "Generation": False
    }
    
    # Run tests
    results["Deblur"] = await test_deblur_agent()
    results["Inpaint"] = await test_inpaint_agent()
    results["Beauty"] = await test_beauty_agent()
    results["Generation"] = await test_generation_agent()
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("📊 Test Summary")
    logger.info("="*70)
    
    for agent, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {agent} Agent")
    
    logger.info("")
    
    total = len(results)
    passed = sum(results.values())
    
    if passed == total:
        logger.info(f"🎉 All tests passed! ({passed}/{total})")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed")
        logger.info("")
        logger.info("📖 Check LOCAL_MODELS_TUTORIAL.md for implementation guide")


async def benchmark_performance():
    """Benchmark all agents"""
    logger.info("\n" + "="*70)
    logger.info("⚡ Performance Benchmark")
    logger.info("="*70)
    
    # Test image
    test_image = Path("test_images/benchmark_sample.jpg")
    
    if not test_image.exists():
        logger.warning("Benchmark image not found")
        return
    
    results = {}
    
    # Benchmark each agent
    agents = [
        ("Deblur", "backend.models.deblur_agent", "deblur_agent"),
        ("Inpaint", "backend.models.inpaint_agent", "inpaint_agent"),
        ("Beauty", "backend.models.beauty_agent", "beauty_agent_gfpgan"),
    ]
    
    for name, module_path, agent_name in agents:
        try:
            module = __import__(module_path, fromlist=[agent_name])
            agent = getattr(module, agent_name)
            
            # Run 3 times and take average
            times = []
            for i in range(3):
                start = time.time()
                await agent.process(test_image)
                elapsed = time.time() - start
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            results[name] = avg_time
            
        except Exception as e:
            logger.error(f"{name}: {e}")
    
    # Display results
    logger.info("")
    logger.info("Average processing time (3 runs):")
    for name, avg_time in sorted(results.items(), key=lambda x: x[1]):
        logger.info(f"  {name:12s}: {avg_time:.2f}s")


def check_environment():
    """Check if environment is ready"""
    logger.info("🔍 Checking environment...")
    logger.info("")
    
    issues = []
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        issues.append("Python 3.8+ required")
    else:
        logger.info(f"✅ Python {python_version.major}.{python_version.minor}")
    
    # Check PyTorch
    try:
        import torch
        logger.info(f"✅ PyTorch {torch.__version__}")
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            logger.info(f"✅ GPU: {gpu_name} ({vram_gb:.1f}GB VRAM)")
        else:
            logger.warning("⚠️  CUDA not available, will use CPU (slow)")
            
    except ImportError:
        issues.append("PyTorch not installed")
    
    # Check models directory
    models_dir = Path("models")
    if not models_dir.exists():
        issues.append("Models directory not found")
        logger.warning("⚠️  Run: python setup_models.py")
    else:
        model_files = list(models_dir.glob("*.pth")) + list(models_dir.glob("*.pt"))
        logger.info(f"✅ Found {len(model_files)} model file(s)")
    
    # Check test images
    test_dir = Path("test_images")
    if not test_dir.exists():
        test_dir.mkdir()
        logger.warning("⚠️  Created test_images/ - please add test images")
    
    logger.info("")
    
    if issues:
        logger.error("❌ Issues found:")
        for issue in issues:
            logger.error(f"   - {issue}")
        return False
    else:
        logger.info("✅ Environment ready!")
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test local model agents")
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run performance benchmark"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check environment only"
    )
    
    args = parser.parse_args()
    
    # Check environment first
    env_ok = check_environment()
    
    if args.check:
        sys.exit(0 if env_ok else 1)
    
    if not env_ok:
        logger.error("Please fix environment issues first")
        sys.exit(1)
    
    # Run tests
    if args.benchmark:
        asyncio.run(benchmark_performance())
    else:
        asyncio.run(test_all())
