import pytesseract
from flask import Flask, request, redirect, url_for, flash, render_template_string
import os
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import requests
import json

# Set path to Tesseract if needed
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # Update if on Windows/Linux

# Hugging Face Token (must have inference access)
HUGGINGFACE_API_KEY = "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"

app = Flask(__name__)
app.secret_key = "secret123"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image)
        extracted_text += f"\nPage {i+1}:\n{text.strip()}\n"
    return extracted_text

def call_huggingface_inference(prompt):
    api_url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
    }
    payload = {"inputs": prompt}
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF Uploader with OCR & HuggingFace</title>
    <style>
        body { font-family: Arial; padding: 40px; background: #f0f0f0; }
        form { background: white; padding: 20px; border-radius: 8px; width: 300px; margin: auto; }
        textarea, pre { width: 90%; margin: 20px auto; display: block; }
        .flash { color: green; text-align: center; }
        h2 { text-align: center; }
    </style>
</head>
<body>
    <h1 style="text-align:center;">Upload a PDF Bill</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="flash">{{ messages[0] }}</div>
      {% endif %}
    {% endwith %}
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="pdf_file" accept=".pdf" required><br><br>
        <input type="submit" value="Upload & Process">
    </form>

    {% if extracted_text %}
        <h2>Raw OCR Text:</h2>
        <pre>{{ extracted_text }}</pre>
        <h2>Structured Extracted Data (via Hugging Face):</h2>
        <pre>{{ structured_data }}</pre>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    extracted_text = ""
    structured_data = ""
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            flash('File uploaded successfully!')

            try:
                # Step 1: OCR
                extracted_text = extract_text_from_pdf(file_path)

                # Step 2: Prompt
                prompt = f"""
You are an AI that extracts structured information from OCR invoice text.
Return only a valid JSON object with the following fields:
"vendor", "invoice_date", "invoice_number", "total_amount", and "items" (a list with "description", "quantity", "price").

Text:
{extracted_text}

Output only JSON.
"""

                # Step 3: Inference
                result = call_huggingface_inference(prompt)
                raw_output = result[0]['generated_text'] if isinstance(result, list) else str(result)

                # Step 4: Try parsing JSON
                try:
                    parsed_json = json.loads(raw_output)
                    structured_data = json.dumps(parsed_json, indent=4)
                except:
                    structured_data = f"⚠️ Unable to parse as JSON:\n{raw_output}"

            except Exception as e:
                structured_data = f"❌ Error: {e}"

    return render_template_string(HTML_TEMPLATE, extracted_text=extracted_text, structured_data=structured_data)

if __name__ == '__main__':
    app.run(debug=True, port=5005)