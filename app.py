from flask import Flask, request, render_template_string
import fitz  # PyMuPDF
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "extracted_txt"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HTML Template
HTML_FORM = """
<h2>Upload a PDF Bill</h2>
<form method="POST" enctype="multipart/form-data">
    <input type="file" name="pdf" accept="application/pdf">
    <input type="submit" value="Upload">
</form>

{% if text %}
<h3>Extracted Text:</h3>
<pre>{{ text }}</pre>
{% endif %}
"""

@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
    text = ""
    if request.method == 'POST':
        pdf_file = request.files.get('pdf')
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            # Extract text
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            for page_num, page in enumerate(doc, start=1):
                text += f"\n--- Page {page_num} ---\n"
                text += page.get_text()
            
            # Save to a .txt file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"extracted_{timestamp}.txt"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

    return render_template_string(HTML_FORM, text=text)

if __name__ == '__main__':
    app.run(debug=True)
