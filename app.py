import pytesseract
from flask import Flask, request, redirect, url_for, flash, render_template_string
import os
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path

# Set Tesseract path if needed (for OCR on images)
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

app = Flask(__name__)
app.secret_key = "secret123"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF Uploader with OCR</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 50px;
            background-color: #f3f3f3;
            text-align: center;
        }
        form {
            margin: 20px auto;
            padding: 20px;
            border: 2px dashed #ccc;
            background-color: white;
            width: 300px;
        }
        textarea {
            width: 80%;
            height: 200px;
            margin-top: 20px;
        }
        .flash {
            color: green;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>Upload a PDF Bill</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="flash">{{ messages[0] }}</div>
      {% endif %}
    {% endwith %}
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="pdf_file" accept=".pdf" required>
        <br>
        <input type="submit" value="Upload & Extract Text">
    </form>

    {% if extracted_text %}
        <h2>Extracted Raw Text:</h2>
        <textarea readonly>{{ extracted_text }}</textarea>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    extracted_text = ""
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

            # Convert PDF to images
            try:
                images = convert_from_path(file_path)
                text_chunks = []
                for i, image in enumerate(images):
                    # OCR using Tesseract
                    text = pytesseract.image_to_string(image)
                    text_chunks.append(f"--- Page {i+1} ---\n{text.strip()}")
                extracted_text = "\n\n".join(text_chunks)
            except Exception as e:
                extracted_text = f"Error processing PDF: {e}"

    return render_template_string(HTML_TEMPLATE, extracted_text=extracted_text)

if __name__ == '__main__':
    app.run(debug=True, port=5005)
