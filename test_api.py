"""
Test script for Deep Vision server API
"""

import requests
import os
from PIL import Image
import numpy as np
import io

# Server URL
BASE_URL = "http://localhost:5000"

def create_test_image():
    """Create a simple test image"""
    # Create a 200x200 colored image
    img_array = np.zeros((200, 200, 3), dtype=np.uint8)
    img_array[:100, :, 0] = 255  # Red top half
    img_array[100:, :, 2] = 255  # Blue bottom half
    
    img = Image.fromarray(img_array)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def test_operations_endpoint():
    """Test getting available operations"""
    print("Testing /api/operations endpoint...")
    response = requests.get(f"{BASE_URL}/api/operations")
    
    if response.status_code == 200:
        operations = response.json()
        print(f"✓ Found {len(operations)} operations")
        for op in operations:
            print(f"  - {op['label']} ({op['name']})")
        return True
    else:
        print(f"✗ Failed: {response.status_code}")
        return False

def test_upload_endpoint():
    """Test image upload"""
    print("\nTesting /api/upload endpoint...")
    
    img_bytes = create_test_image()
    files = {'file': ('test_image.png', img_bytes, 'image/png')}
    
    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✓ Upload successful: {data.get('filename')}")
            return data.get('filename')
        else:
            print(f"✗ Upload failed: {data.get('error')}")
            return None
    else:
        print(f"✗ Failed: {response.status_code}")
        return None

def test_process_endpoint(filename):
    """Test image processing"""
    print("\nTesting /api/process endpoint...")
    
    operations_to_test = [
        {'operation': 'grayscale', 'params': {}},
        {'operation': 'blur', 'params': {'strength': 5}},
        {'operation': 'sharpen', 'params': {}},
    ]
    
    for test in operations_to_test:
        payload = {
            'filename': filename,
            'operation': test['operation'],
            'params': test['params']
        }
        
        response = requests.post(
            f"{BASE_URL}/api/process",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ {test['operation']}: {data.get('filename')}")
            else:
                print(f"✗ {test['operation']} failed: {data.get('error')}")
        else:
            print(f"✗ {test['operation']} failed: {response.status_code}")

def test_download_endpoint(filename):
    """Test image download"""
    print("\nTesting /api/download endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/download/{filename}")
    
    if response.status_code == 200:
        print(f"✓ Download successful: {len(response.content)} bytes")
        return True
    else:
        print(f"✗ Failed: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Deep Vision Server API Tests")
    print("=" * 50)
    print(f"Server URL: {BASE_URL}")
    print("=" * 50)
    
    # Check if server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.RequestException:
        print("\n✗ Server is not running!")
        print("Please start the server with: python server.py")
        return
    
    # Run tests
    test_operations_endpoint()
    
    filename = test_upload_endpoint()
    if filename:
        test_process_endpoint(filename)
        test_download_endpoint(filename)
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
