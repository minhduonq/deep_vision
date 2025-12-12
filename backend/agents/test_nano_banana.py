"""
Test script cho Nano Banana Agent
Sử dụng Google Nano Banana từ Replicate để chỉnh sửa ảnh
"""
import asyncio
from pathlib import Path
from backend.agents.nano_banana_agent import nano_banana_agent
from loguru import logger

# Test data
TEST_IMAGE = "../../test_images/sample.jpg"  # Thay đổi path theo ảnh test của bạn
TEST_OUTPUT_DIR = "../../outputs"

async def test_edit_image():
    """Test chỉnh sửa ảnh cơ bản"""
    logger.info("\n=== Test: Edit Image ===")
    
    result = await nano_banana_agent.edit_image(
        image_path=TEST_IMAGE,
        prompt="Make the scene more vibrant and colorful, enhance lighting",
        output_dir=TEST_OUTPUT_DIR
    )
    
    if result["success"]:
        logger.success(f"✅ Edit successful!")
        logger.info(f"Output: {result['output_path']}")
        logger.info(f"Metadata: {result['metadata']}")
    else:
        logger.error(f"❌ Edit failed: {result.get('error')}")
    
    return result

async def test_edit_with_multiple_images():
    """Test chỉnh sửa với nhiều ảnh input"""
    logger.info("\n=== Test: Edit Multiple Images ===")
    
    # Giả sử có 2 ảnh để test
    images = [TEST_IMAGE, TEST_IMAGE]  # Trong thực tế, dùng 2 ảnh khác nhau
    
    result = await nano_banana_agent.edit_image(
        image_path=images,
        prompt="Make the sheets in the style of the logo. Make the scene natural.",
        output_dir=TEST_OUTPUT_DIR
    )
    
    if result["success"]:
        logger.success(f"✅ Edit with multiple images successful!")
        logger.info(f"Output: {result['output_path']}")
        logger.info(f"Number of input images: {result['num_images']}")
    else:
        logger.error(f"❌ Edit failed: {result.get('error')}")
    
    return result

async def test_style_transfer():
    """Test chuyển đổi style"""
    logger.info("\n=== Test: Style Transfer ===")
    
    result = await nano_banana_agent.style_transfer(
        image_path=TEST_IMAGE,
        style="anime art",
        output_dir=TEST_OUTPUT_DIR
    )
    
    if result["success"]:
        logger.success(f"✅ Style transfer successful!")
        logger.info(f"Output: {result['output_path']}")
    else:
        logger.error(f"❌ Style transfer failed: {result.get('error')}")
    
    return result

async def test_beauty_enhance():
    """Test làm đẹp ảnh"""
    logger.info("\n=== Test: Beauty Enhancement ===")
    
    result = await nano_banana_agent.beauty_enhance(
        image_path=TEST_IMAGE,
        level="natural",
        output_dir=TEST_OUTPUT_DIR
    )
    
    if result["success"]:
        logger.success(f"✅ Beauty enhancement successful!")
        logger.info(f"Output: {result['output_path']}")
    else:
        logger.error(f"❌ Beauty enhancement failed: {result.get('error')}")
    
    return result

async def test_remove_object():
    """Test xóa object"""
    logger.info("\n=== Test: Remove Object ===")
    
    result = await nano_banana_agent.remove_object(
        image_path=TEST_IMAGE,
        object_description="watermark",
        output_dir=TEST_OUTPUT_DIR
    )
    
    if result["success"]:
        logger.success(f"✅ Object removal successful!")
        logger.info(f"Output: {result['output_path']}")
    else:
        logger.error(f"❌ Object removal failed: {result.get('error')}")
    
    return result

async def test_process_edit_request():
    """Test method dùng cho orchestrator integration"""
    logger.info("\n=== Test: Process Edit Request (Orchestrator Interface) ===")
    
    result = await nano_banana_agent.process_edit_request(
        image_path=TEST_IMAGE,
        prompt="Change the background to a beautiful sunset scene",
        output_dir=TEST_OUTPUT_DIR,
        aspect_ratio="16:9",
        output_format="jpg"
    )
    
    if result["success"]:
        logger.success(f"✅ Edit request processed successfully!")
        logger.info(f"Output: {result['output_path']}")
    else:
        logger.error(f"❌ Edit request failed: {result.get('error')}")
    
    return result

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Nano Banana Agent Tests")
    logger.info("=" * 60)
    
    # Kiểm tra REPLICATE_API_TOKEN
    import os
    if not os.getenv("REPLICATE_API_TOKEN"):
        logger.error("❌ REPLICATE_API_TOKEN not set!")
        logger.info("Please set: export REPLICATE_API_TOKEN=your_token_here")
        return
    
    # Kiểm tra test image exists
    if not Path(TEST_IMAGE).exists():
        logger.error(f"❌ Test image not found: {TEST_IMAGE}")
        logger.info("Please update TEST_IMAGE path in this script")
        return
    
    try:
        # Run tests
        await test_edit_image()
        await asyncio.sleep(2)  # Rate limiting
        
        # Uncomment để test thêm các features khác
        # await test_style_transfer()
        # await asyncio.sleep(2)
        
        # await test_beauty_enhance()
        # await asyncio.sleep(2)
        
        # await test_remove_object()
        # await asyncio.sleep(2)
        
        await test_process_edit_request()
        
        logger.success("\n✅ All tests completed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
