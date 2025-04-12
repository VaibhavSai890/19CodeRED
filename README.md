 🧾 GenAI-Powered Smart Bill Organizer

A desktop application that uses GenAI and OCR to extract, classify, and organize information from unstructured PDF bills (Employee, Pharmaceutical, and Insurance bills) into neatly structured and categorized tables using a user-friendly GUI.

---

## 🚀 Features

- 📤 *Upload PDF Bills*: Easily upload scanned or generated bills in PDF format.
- 🧠 *GenAI-Powered Classification*: Automatically classifies bills into:
  - Employee Bills
  - Pharmaceutical Bills
  - Insurance Bills
- 🔍 *Information Extraction*: Parses key details (e.g., Name, Address, Invoice Number, Claim Number, etc.) from unstructured data using regex.
- 📊 *Categorized Display*: Displays all extracted information in categorized, scrollable tables using Tkinter.
- 📁 *Organized Storage*: Automatically moves files into respective folders under /uploads based on their category.

---

## 🛠️ Technologies Used

- *Python 3.8+*
- *Tkinter* – GUI Framework
- *PyPDF2* – For extracting text from PDF
- *Transformers (Hugging Face)* – For zero-shot classification (facebook/bart-large-mnli)
- *Regex* – For extracting structured fields
- *shutil / os* – For organizing uploaded files

---

## 📦 Installation

```bash
cd genai-bill-organizer
pip install -r requirements.txt
