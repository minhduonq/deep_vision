"""
Simple API Test - Minimal Example
Quick test for Deep Vision API with image upload
"""
import requests
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
IMAGE_PATH = "test_images/sample.jpg"  # Change this to your image

def simple_test():
    """Simple one-function test"""
    
    print("🔍 Testing Deep Vision API\n")
    
    # 1. Check if image exists
    if not Path(IMAGE_PATH).exists():
        print(f"❌ Image not found: {IMAGE_PATH}")
        print("\n💡 To fix:")
        print(f"   1. Create 'test_images' folder")
        print(f"   2. Place an image there")
        print(f"   3. Update IMAGE_PATH in this script")
        return
    
    # 2. Open and send the image
    print(f"📁 Uploading: {IMAGE_PATH}")
    
    with open(IMAGE_PATH, 'rb') as image_file:
        # Prepare the request
        files = {
            'file': (Path(IMAGE_PATH).name, image_file, 'image/jpeg')
        }
        data = {
            'task_type': 'deblur',  # Options: deblur, inpaint, beauty_enhance
            'description': 'Test enhancement'
        }
        
        # Send request
        response = requests.post(
            f"{API_URL}/api/v1/enhance",
            files=files,
            data=data,
            timeout=30
        )
    
    # 3. Check response
    if response.status_code == 200:
        result = response.json()
        task_id = result['task_id']
        
        print(f"✅ Success! Task ID: {task_id}")
        print(f"\n📊 Full Response:")
        print(result)
        
        print(f"\n💡 Check status:")
        print(f"   GET {API_URL}/api/v1/status/{task_id}")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")


if __name__ == "__main__":
    simple_test()
