"""
Deep Vision - Image Editing Server
A Flask-based server for deep learning-powered image editing
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import io
from PIL import Image
import numpy as np
import cv2

# Optional: PyTorch for advanced deep learning features
try:
    import torch
    import torchvision.transforms as transforms
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("PyTorch not installed. Advanced deep learning features disabled.")

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def apply_grayscale(image):
    """Convert image to grayscale"""
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)


def apply_blur(image, strength=15):
    """Apply Gaussian blur to image"""
    img_array = np.array(image)
    kernel_size = int(strength) * 2 + 1
    return cv2.GaussianBlur(img_array, (kernel_size, kernel_size), 0)


def apply_sharpen(image):
    """Sharpen the image"""
    img_array = np.array(image)
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    return cv2.filter2D(img_array, -1, kernel)


def apply_edge_detection(image):
    """Apply Canny edge detection"""
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)


def apply_sepia(image):
    """Apply sepia tone filter"""
    img_array = np.array(image).astype(np.float32)
    sepia_filter = np.array([[0.393, 0.769, 0.189],
                             [0.349, 0.686, 0.168],
                             [0.272, 0.534, 0.131]])
    sepia_img = cv2.transform(img_array, sepia_filter)
    sepia_img = np.clip(sepia_img, 0, 255)
    return sepia_img.astype(np.uint8)


def apply_brightness(image, factor=1.5):
    """Adjust image brightness"""
    img_array = np.array(image).astype(np.float32)
    bright_img = img_array * factor
    bright_img = np.clip(bright_img, 0, 255)
    return bright_img.astype(np.uint8)


def apply_contrast(image, factor=1.5):
    """Adjust image contrast"""
    img_array = np.array(image).astype(np.float32)
    mean = img_array.mean()
    contrast_img = (img_array - mean) * factor + mean
    contrast_img = np.clip(contrast_img, 0, 255)
    return contrast_img.astype(np.uint8)


def apply_invert(image):
    """Invert image colors"""
    img_array = np.array(image)
    return 255 - img_array


def apply_cartoon(image):
    """Apply cartoon effect"""
    img_array = np.array(image)
    # Convert to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    # Apply median blur
    gray = cv2.medianBlur(gray, 5)
    # Detect edges
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY, 9, 9)
    # Smooth the image
    color = cv2.bilateralFilter(img_array, 9, 250, 250)
    # Combine edges and color
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon


def apply_emboss(image):
    """Apply emboss effect"""
    img_array = np.array(image)
    kernel = np.array([[-2, -1, 0],
                       [-1,  1, 1],
                       [ 0,  1, 2]])
    embossed = cv2.filter2D(img_array, -1, kernel)
    # Normalize to 0-255
    embossed = cv2.normalize(embossed, None, 0, 255, cv2.NORM_MINMAX)
    return embossed


@app.route('/')
def index():
    """Serve the main page"""
    return send_file('static/index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'File uploaded successfully'
        }), 200
    
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/api/process', methods=['POST'])
def process_image():
    """Process image with specified filter/effect"""
    data = request.get_json()
    
    if not data or 'filename' not in data or 'operation' not in data:
        return jsonify({'error': 'Missing filename or operation'}), 400
    
    filename = secure_filename(data['filename'])
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Load image
        image = Image.open(filepath)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        operation = data['operation']
        params = data.get('params', {})
        
        # Apply the requested operation
        if operation == 'grayscale':
            result = apply_grayscale(image)
            result = Image.fromarray(result).convert('RGB')
        elif operation == 'blur':
            strength = params.get('strength', 5)
            result = apply_blur(image, strength)
            result = Image.fromarray(result)
        elif operation == 'sharpen':
            result = apply_sharpen(image)
            result = Image.fromarray(result)
        elif operation == 'edge_detection':
            result = apply_edge_detection(image)
            result = Image.fromarray(result)
        elif operation == 'sepia':
            result = apply_sepia(image)
            result = Image.fromarray(result)
        elif operation == 'brightness':
            factor = params.get('factor', 1.5)
            result = apply_brightness(image, factor)
            result = Image.fromarray(result)
        elif operation == 'contrast':
            factor = params.get('factor', 1.5)
            result = apply_contrast(image, factor)
            result = Image.fromarray(result)
        elif operation == 'invert':
            result = apply_invert(image)
            result = Image.fromarray(result)
        elif operation == 'cartoon':
            result = apply_cartoon(image)
            result = Image.fromarray(result)
        elif operation == 'emboss':
            result = apply_emboss(image)
            result = Image.fromarray(result)
        else:
            return jsonify({'error': 'Unknown operation'}), 400
        
        # Save processed image
        output_filename = f"processed_{filename}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        result.save(output_path)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'message': 'Image processed successfully'
        }), 200
        
    except Exception as e:
        # Log the error internally but don't expose stack trace to users
        app.logger.error(f"Error processing image: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the image'}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download processed image"""
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, mimetype='image/jpeg')


@app.route('/api/operations', methods=['GET'])
def get_operations():
    """Get list of available operations"""
    operations = [
        {'name': 'grayscale', 'label': 'Grayscale', 'params': []},
        {'name': 'blur', 'label': 'Blur', 'params': [
            {'name': 'strength', 'type': 'number', 'default': 5, 'min': 1, 'max': 20}
        ]},
        {'name': 'sharpen', 'label': 'Sharpen', 'params': []},
        {'name': 'edge_detection', 'label': 'Edge Detection', 'params': []},
        {'name': 'sepia', 'label': 'Sepia Tone', 'params': []},
        {'name': 'brightness', 'label': 'Brightness', 'params': [
            {'name': 'factor', 'type': 'number', 'default': 1.5, 'min': 0.1, 'max': 3.0, 'step': 0.1}
        ]},
        {'name': 'contrast', 'label': 'Contrast', 'params': [
            {'name': 'factor', 'type': 'number', 'default': 1.5, 'min': 0.1, 'max': 3.0, 'step': 0.1}
        ]},
        {'name': 'invert', 'label': 'Invert Colors', 'params': []},
        {'name': 'cartoon', 'label': 'Cartoon Effect', 'params': []},
        {'name': 'emboss', 'label': 'Emboss', 'params': []},
    ]
    return jsonify(operations)


if __name__ == '__main__':
    print("Starting Deep Vision Image Editing Server...")
    print("Server running at http://localhost:5000")
    print("WARNING: This is a development server. Use a production WSGI server for deployment.")
    
    # Debug mode should be disabled in production
    # Set debug=False and use proper logging instead
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
