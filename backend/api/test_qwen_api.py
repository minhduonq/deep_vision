"""
Test script for new Qwen Edit API endpoints
"""
import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"


def test_fast_edit():
    """Test fast single image edit"""
    print("\n=== Testing Fast Edit ===")
    
    # Upload image and edit
    with open("test_images/sample.jpg", "rb") as f:
        files = {"file": f}
        data = {
            "prompt": "Change the color to vibrant blue",
            "guidance_scale": 1.0,
            "steps": 8
        }
        
        response = requests.post(f"{BASE_URL}/edit/fast", files=files, data=data)
        
    if response.status_code == 200:
        result = response.json()
        task_id = result["task_id"]
        print(f"✅ Task created: {task_id}")
        
        # Poll for result
        return poll_task(task_id)
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None


def test_fusion_edit():
    """Test fusion edit with 2 images"""
    print("\n=== Testing Fusion Edit ===")
    
    with open("test_images/image1.jpg", "rb") as f1, \
         open("test_images/image2.jpg", "rb") as f2:
        
        files = {
            "image_1": f1,
            "image_2": f2
        }
        data = {
            "prompt": "Replace the glasses in image 2 with glasses from image 1",
            "lora_adapter": "Super-Fusion",
            "guidance_scale": 1.0,
            "steps": 4
        }
        
        response = requests.post(f"{BASE_URL}/edit/fusion", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        task_id = result["task_id"]
        print(f"✅ Task created: {task_id}")
        
        return poll_task(task_id)
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None


def test_list_lora_styles():
    """List available LoRA styles"""
    print("\n=== Available LoRA Styles ===")
    
    response = requests.get(f"{BASE_URL}/edit/lora-styles")
    
    if response.status_code == 200:
        styles = response.json()["styles"]
        for style in styles:
            print(f"• {style['name']}: {style['description']}")
    else:
        print(f"❌ Error: {response.status_code}")


def poll_task(task_id: str, max_attempts: int = 60) -> dict:
    """Poll task status until completion"""
    print(f"Polling task {task_id}...")
    
    for i in range(max_attempts):
        response = requests.get(f"{BASE_URL}/status/{task_id}")
        
        if response.status_code == 200:
            status = response.json()
            print(f"  [{i+1}/{max_attempts}] Status: {status['status']} - Progress: {status['progress']}%")
            
            if status["status"] == "completed":
                print(f"✅ Task completed!")
                print(f"   Result URL: {status.get('result_url')}")
                
                # Download result
                download_result(task_id)
                return status
                
            elif status["status"] == "failed":
                print(f"❌ Task failed: {status.get('error')}")
                return status
            
        time.sleep(2)
    
    print("⚠️ Timeout waiting for task")
    return None


def download_result(task_id: str, output_dir: str = "outputs"):
    """Download result image"""
    Path(output_dir).mkdir(exist_ok=True)
    
    response = requests.get(f"{BASE_URL}/result/{task_id}")
    
    if response.status_code == 200:
        output_path = Path(output_dir) / f"{task_id}_result.png"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"   Downloaded to: {output_path}")
    else:
        print(f"   Failed to download: {response.status_code}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING QWEN EDIT API ENDPOINTS")
    print("=" * 60)
    
    # Test 1: List LoRA styles
    test_list_lora_styles()
    
    # Test 2: Fast edit (uncomment to run)
    # test_fast_edit()
    
    # Test 3: Fusion edit (uncomment to run)
    # test_fusion_edit()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
