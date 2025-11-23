"""
Deep Vision - Streamlit Frontend
Simple web interface for the Deep Vision API
"""
import streamlit as st
import requests
from PIL import Image
import io
import time
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Deep Vision",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = st.sidebar.text_input(
    "API URL", 
    value="http://localhost:8000",
    help="Base URL of the Deep Vision API"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .task-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎨 Deep Vision</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Multi-Agent AI Image Processing System</p>', unsafe_allow_html=True)

# Check API health
def check_api_health():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        return False, str(e)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Status
    api_status, api_info = check_api_health()
    if api_status:
        st.success("✅ API Connected")
        if api_info:
            with st.expander("API Info"):
                st.json(api_info)
    else:
        st.error("❌ API Not Available")
        st.info("Make sure the API server is running:\n```python backend/api/main.py```")
    
    st.markdown("---")
    
    # Task Type Selection
    task_mode = st.selectbox(
        "Select Mode",
        ["🖼️ Image Enhancement", "🎨 Image Generation"],
        help="Choose between enhancing existing images or generating new ones"
    )

# Main content area
if "🖼️" in task_mode:
    # ==================== IMAGE ENHANCEMENT ====================
    st.header("📸 Image Enhancement")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Input")
        
        # Enhancement type selection
        enhancement_type = st.selectbox(
            "Enhancement Type",
            ["deblur", "inpaint", "beauty_enhance"],
            format_func=lambda x: {
                "deblur": "🔍 Deblur / Sharpen",
                "inpaint": "✂️ Remove Objects",
                "beauty_enhance": "✨ Beauty Enhancement"
            }[x]
        )
        
        # Description
        description = st.text_area(
            "Description (optional)",
            placeholder="Describe what you want to enhance or remove...",
            help="Provide additional context for better results"
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload an image to enhance"
        )
        
        if uploaded_file:
            # Display original image
            image = Image.open(uploaded_file)
            st.image(image, caption="Original Image", use_container_width=True)
            
            # Image info
            st.info(f"📊 Size: {image.size[0]}x{image.size[1]} | Format: {image.format}")
    
    with col2:
        st.subheader("Output")
        
        if uploaded_file:
            if st.button("🚀 Process Image", type="primary", use_container_width=True):
                if not api_status:
                    st.error("API is not available. Please check the connection.")
                else:
                    with st.spinner("Processing image..."):
                        try:
                            # Prepare files
                            uploaded_file.seek(0)  # Reset file pointer
                            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                            data = {
                                "task_type": enhancement_type,
                                "description": description or ""
                            }
                            
                            # Submit task
                            response = requests.post(
                                f"{API_BASE_URL}/api/v1/enhance",
                                files=files,
                                data=data,
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                task_id = result["task_id"]
                                
                                st.success(f"✅ Task created: {task_id}")
                                
                                # Poll for result
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                max_wait = 120  # 2 minutes
                                elapsed = 0
                                
                                while elapsed < max_wait:
                                    status_response = requests.get(
                                        f"{API_BASE_URL}/api/v1/status/{task_id}"
                                    )
                                    
                                    if status_response.status_code == 200:
                                        status_data = status_response.json()
                                        status = status_data["status"]
                                        progress = status_data.get("progress", 0)
                                        
                                        progress_bar.progress(int(progress))
                                        status_text.text(f"Status: {status} ({progress:.0f}%)")
                                        
                                        if status == "completed":
                                            # Get result
                                            result_url = status_data.get("result_url")
                                            if result_url:
                                                result_image_url = f"{API_BASE_URL}{result_url}"
                                                result_image_response = requests.get(result_image_url)
                                                
                                                if result_image_response.status_code == 200:
                                                    result_image = Image.open(io.BytesIO(result_image_response.content))
                                                    st.image(result_image, caption="Enhanced Image", use_container_width=True)
                                                    
                                                    # Download button
                                                    st.download_button(
                                                        label="⬇️ Download Result",
                                                        data=result_image_response.content,
                                                        file_name=f"enhanced_{uploaded_file.name}",
                                                        mime="image/png"
                                                    )
                                            break
                                        
                                        elif status == "failed":
                                            error = status_data.get("error", "Unknown error")
                                            st.error(f"❌ Processing failed: {error}")
                                            break
                                    
                                    time.sleep(2)
                                    elapsed += 2
                                
                                if elapsed >= max_wait:
                                    st.warning("⏱️ Processing is taking longer than expected. Check status manually.")
                            
                            else:
                                st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        else:
            st.info("👆 Upload an image to get started")

else:
    # ==================== IMAGE GENERATION ====================
    st.header("🎨 Image Generation")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Settings")
        
        # Prompt
        prompt = st.text_area(
            "Prompt",
            placeholder="A beautiful sunset over mountains, digital art, highly detailed...",
            height=100,
            help="Describe the image you want to generate"
        )
        
        # Negative prompt
        negative_prompt = st.text_input(
            "Negative Prompt (optional)",
            placeholder="blurry, low quality, distorted...",
            help="What to avoid in the generated image"
        )
        
        # Advanced settings
        with st.expander("⚙️ Advanced Settings"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                width = st.select_slider(
                    "Width",
                    options=[256, 384, 512, 640, 768, 896, 1024],
                    value=512
                )
                
                num_images = st.slider(
                    "Number of Images",
                    min_value=1,
                    max_value=4,
                    value=1
                )
            
            with col_b:
                height = st.select_slider(
                    "Height",
                    options=[256, 384, 512, 640, 768, 896, 1024],
                    value=512
                )
                
                guidance_scale = st.slider(
                    "Guidance Scale",
                    min_value=1.0,
                    max_value=20.0,
                    value=7.5,
                    step=0.5
                )
            
            num_inference_steps = st.slider(
                "Inference Steps",
                min_value=10,
                max_value=150,
                value=50,
                step=10
            )
            
            seed = st.number_input(
                "Seed (optional, -1 for random)",
                min_value=-1,
                max_value=2147483647,
                value=-1
            )
    
    with col2:
        st.subheader("Generated Images")
        
        if st.button("🎨 Generate", type="primary", use_container_width=True):
            if not prompt:
                st.warning("⚠️ Please enter a prompt")
            elif not api_status:
                st.error("❌ API is not available")
            else:
                with st.spinner("Generating image..."):
                    try:
                        # Prepare request
                        payload = {
                            "prompt": prompt,
                            "negative_prompt": negative_prompt or None,
                            "num_images": num_images,
                            "width": width,
                            "height": height,
                            "guidance_scale": guidance_scale,
                            "num_inference_steps": num_inference_steps,
                            "seed": seed if seed != -1 else None
                        }
                        
                        # Submit task
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/generate",
                            json=payload,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            task_id = result["task_id"]
                            
                            st.success(f"✅ Task created: {task_id}")
                            st.info("⏳ This feature will be fully implemented soon. Currently, tasks are created but not processed.")
                            
                            # TODO: Implement polling for generation results
                            # Similar to enhancement polling
                        
                        else:
                            st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Deep Vision v0.1.0**")
with col2:
    st.markdown("Multi-Agent Computer Vision System")
with col3:
    st.markdown("[Documentation](#) | [GitHub](#)")
