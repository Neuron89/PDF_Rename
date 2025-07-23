import os
import re
import pytesseract
from pdf2image import convert_from_path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import json
import tempfile
import shutil
from PIL import Image
import base64
import io
import webbrowser
import threading
import sys

if getattr(sys, 'frozen', False):
    # Running in a bundle
    BASE_DIR = sys._MEIPASS
else:
    # Running in normal Python
    BASE_DIR = os.getcwd()

INTERNAL_DIR = os.path.join(BASE_DIR, '.internal')
UPLOAD_FOLDER = os.path.join(INTERNAL_DIR, 'uploads')
TEMP_FOLDER = os.path.join(INTERNAL_DIR, 'temp')
TEMPLATES_FOLDER = os.path.join(INTERNAL_DIR, 'templates')
POPLER_PATH = os.path.join(INTERNAL_DIR, 'poppler', 'bin')
TESSERACT_PATH = os.path.join(INTERNAL_DIR, 'tesseract', 'tesseract.exe')

app = Flask(__name__, template_folder=TEMPLATES_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# CONFIG
poppler_path = POPLER_PATH  # Poppler bin path inside .internal
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Regex patterns
doc_regex = r"DOCUMENT NO:\s*([A-Z]+[0-9]+)"
item_regex = r"FG ITEM\s*#\s*([A-Z0-9_-]+)"

def extract_text_from_region(image, x, y, width, height):
    """Extract text from a specific region of the image"""
    try:
        # Crop the image to the specified region
        cropped = image.crop((x, y, x + width, y + height))
        # Extract text from the cropped region
        text = pytesseract.image_to_string(cropped)
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def process_pdf_with_regions(pdf_path, regions, rename_pattern):
    """Process PDF with custom regions and rename pattern"""
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        if not images:
            return {"error": "No images extracted from PDF"}
        
        # Extract text from each region
        extracted_data = {}
        for region_name, region_coords in regions.items():
            x, y, width, height = region_coords
            text = extract_text_from_region(images[0], x, y, width, height)
            # Replace newlines with underscores
            text = text.replace('\n', '_').replace('\r', '_')
            extracted_data[region_name] = text
        
        # Generate new filename based on pattern
        new_filename = rename_pattern
        for region_name, text in extracted_data.items():
            placeholder = f"{{{region_name}}}"
            new_filename = new_filename.replace(placeholder, text)
        
        # Clean filename (remove invalid characters)
        new_filename = re.sub(r'[<>:"/\\|?*]', '_', new_filename)
        new_filename = f"{new_filename}.pdf"
        
        return {
            "success": True,
            "extracted_data": extracted_data,
            "new_filename": new_filename,
            "original_filename": os.path.basename(pdf_path)
        }
        
    except Exception as e:
        return {"error": f"Error processing PDF: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"})
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"})
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Convert first page to image for region selection
        images = convert_from_path(filepath, poppler_path=poppler_path)
        if images:
            # Save first page as image
            img_path = os.path.join(app.config['TEMP_FOLDER'], f"{filename}_preview.png")
            images[0].save(img_path, 'PNG')
            
            # Convert to base64 for display
            with open(img_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
            
            return jsonify({
                "success": True,
                "filename": filename,
                "preview_image": f"data:image/png;base64,{img_data}",
                "image_width": images[0].width,
                "image_height": images[0].height
            })
        else:
            return jsonify({"error": "Could not extract images from PDF"})
            
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"})

@app.route('/process', methods=['POST'])
def process_file():
    data = request.json
    filename = data.get('filename')
    regions = data.get('regions', {})
    rename_pattern = data.get('rename_pattern', '')
    
    if not filename or not regions or not rename_pattern:
        return jsonify({"error": "Missing required data"})
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"})
    
    result = process_pdf_with_regions(filepath, regions, rename_pattern)
    
    if result.get("success"):
        # Rename the file
        new_filepath = os.path.join(app.config['UPLOAD_FOLDER'], result["new_filename"])
        try:
            os.rename(filepath, new_filepath)
            result["file_renamed"] = True
        except Exception as e:
            result["file_renamed"] = False
            result["rename_error"] = str(e)
    
    return jsonify(result)

@app.route('/process_folder', methods=['POST'])
def process_folder():
    data = request.json
    regions = data.get('regions', {})
    rename_pattern = data.get('rename_pattern', '')
    input_folder = os.path.join(os.getcwd(), 'PDFs to rename')
    output_folder = os.path.join(os.getcwd(), 'Renamed PDFs')
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    if not os.path.exists(input_folder):
        return jsonify({"error": "PDFs to rename folder not found"})
    results = []
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.pdf'):
            filepath = os.path.join(input_folder, filename)
            result = process_pdf_with_regions(filepath, regions, rename_pattern)
            if result.get("success"):
                new_filename = result["new_filename"]
                new_filepath = os.path.join(output_folder, new_filename)
                try:
                    shutil.copy2(filepath, filepath.replace('.pdf', '_before_rename.pdf'))
                    shutil.move(filepath, new_filepath)
                    result["file_renamed"] = True
                except Exception as e:
                    result["file_renamed"] = False
                    result["rename_error"] = str(e)
            result["original_filename"] = filename
            results.append(result)
    return jsonify({"results": results})

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"})

if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000/')
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True, host='127.0.0.1', port=5000)
