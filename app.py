from flask import Flask, request, render_template_string
import fitz  # PyMuPDF

app = Flask(__name__)

HTML_FORM = """
<h2>Upload a PDF bill</h2>
<form method="POST" enctype="multipart/form-data">
    <input type="file" name="pdf">
    <input type="submit">
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
        pdf_file = request.files['pdf']
        if pdf_file:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            for page in doc:
                text += page.get_text()
    return render_template_string(HTML_FORM, text=text)

if __name__ == '__main__':
    app.run(debug=True)
