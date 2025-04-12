import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from transformers import pipeline
import os
from PyPDF2 import PdfReader


# Initialize Hugging Face zero-shot-classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Categories to classify the text into
candidate_labels = ["Employee Bill", "Pharmaceutical Bill", "Insurance Bill"]

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def classify_category(text):
    """Classify the extracted text into categories using Hugging Face."""
    result = classifier(text, candidate_labels)
    return result['labels'][0]  # Return the category with the highest score

def parse_record(record_text):
    lines = [line.strip() for line in record_text.split('\n') if line.strip()]
    record = {}

    known_keys = [
        "name", "address", "phone no", "employee id", "post", "salary", "hours worked",
        "invoice no", "vendor name", "vendor address", "date", "items", "quantity", "cost",
        "insurance number", "company name", "claim number"
    ]

    for line in lines:
        match = re.match(r"^(.*?)(?:\s*[:-]\s*)(.*)$", line)
        if match:
            key = match.group(1).strip().lower().replace(' ', '_')
            value = match.group(2).strip()
            record[key] = value
        else:
            # Try matching known keys without separator
            for key in known_keys:
                if line.lower().startswith(key):
                    value = line[len(key):].strip(" :-")
                    record[key.replace(' ', '_')] = value.strip()
                    break
    return record

def process_file_content(content):
    """Process file content into categorized records."""
    employee_records = []
    pharma_records = []
    insurance_records = []

    raw_records = content.split('--- Page 1 ---')
    for raw in raw_records:
        raw = raw.strip()
        if not raw:
            continue
        record = parse_record(raw)
        cat = record.get('category', '')
        if "insurance bill" in cat.lower():
            insurance_records.append(record)
        elif "employee bill" in cat.lower():
            employee_records.append(record)
        elif "pharmaceutical" in cat.lower() or "equipment" in cat.lower():
            pharma_records.append(record)
    return employee_records, pharma_records, insurance_records

def load_file():
    """Load and process the selected PDF file."""
    filepath = filedialog.askopenfilename(title="Select a PDF File", filetypes=[("PDF Files", "*.pdf")])
    if filepath:
        try:
            # Extract text from the selected PDF
            content = extract_text_from_pdf(filepath)
            
            # Classify the text into categories using Hugging Face
            category = classify_category(content)

            # Process content based on the classification
            emp_records, pharma_records, ins_records = process_file_content(content)

            # Create categorized folders
            categorized_folder = os.path.join("uploads", category)
            if not os.path.exists(categorized_folder):
                os.makedirs(categorized_folder)
            
            # Move the PDF to the corresponding category folder
            pdf_name = os.path.basename(filepath)
            destination = os.path.join(categorized_folder, pdf_name)
            os.rename(filepath, destination)

            messagebox.showinfo("Success", f"File classified as {category} and moved to {categorized_folder}!")
            display_tables(emp_records, pharma_records, ins_records)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file:\n{e}")

def clear_tree(tree):
    """Clear the Treeview."""
    for item in tree.get_children():
        tree.delete(item)

def display_tables(emp_records, pharma_records, ins_records):
    """Display categorized data in tables."""
    clear_tree(emp_tree)
    clear_tree(pharma_tree)
    clear_tree(ins_tree)
    
    for rec in emp_records:
        values = (
            rec.get("name", ""),
            rec.get("address", ""),
            rec.get("phone_no", ""),
            rec.get("employee_id", ""),
            rec.get("post", ""),
            rec.get("salary", ""),
            rec.get("hours_worked", "")
        )
        emp_tree.insert("", tk.END, values=values)
        
    for rec in pharma_records:
        values = (
            rec.get("name", ""),
            rec.get("address", ""),
            rec.get("phone_no", ""),
            rec.get("invoice_no", ""),
            rec.get("vendor_name", ""),
            rec.get("vendor_address", ""),
            rec.get("date", ""),
            rec.get("items", ""),
            rec.get("quantity", ""),
            rec.get("cost", "")
        )
        pharma_tree.insert("", tk.END, values=values)
    
    for rec in ins_records:
        values = (
            rec.get("name", ""),
            rec.get("address", ""),
            rec.get("phone_no", ""),
            rec.get("insurance_number", ""),
            rec.get("company_name", ""),
            rec.get("claim_number", ""),
            rec.get("date", "")
        )
        ins_tree.insert("", tk.END, values=values)

# -------------------- GUI Setup --------------------

root = tk.Tk()
root.title("Jumbled Data Arranger")

# Create folder for uploads if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

load_btn = tk.Button(top_frame, text="Load PDF File", command=load_file)
load_btn.pack(side=tk.LEFT, padx=5)

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# --------------------- EMPLOYEE BILL TAB ---------------------
emp_tab = tk.Frame(notebook)
notebook.add(emp_tab, text="Employee Bills")

emp_columns = ("Name", "Address", "Phone No", "Employee ID", "Post", "Salary", "Hours Worked")
emp_tree = ttk.Treeview(emp_tab, columns=emp_columns, show="headings")
for col in emp_columns:
    emp_tree.heading(col, text=col)
    emp_tree.column(col, width=100, anchor=tk.CENTER)
emp_tree.pack(fill=tk.BOTH, expand=True)

# --------------------- PHARMACEUTICAL BILL TAB ---------------------
pharma_tab = tk.Frame(notebook)
notebook.add(pharma_tab, text="Pharmaceutical Bills")

pharma_columns = ("Name", "Address", "Phone No", "Invoice No", "Vendor Name", "Vendor Address", "Date", "Items", "Quantity", "Cost")
pharma_tree = ttk.Treeview(pharma_tab, columns=pharma_columns, show="headings")
for col in pharma_columns:
    pharma_tree.heading(col, text=col)
    pharma_tree.column(col, width=100, anchor=tk.CENTER)
pharma_tree.pack(fill=tk.BOTH, expand=True)

# --------------------- INSURANCE BILL TAB ---------------------
ins_tab = tk.Frame(notebook)
notebook.add(ins_tab, text="Insurance Bills")

ins_columns = ("Name", "Address", "Phone No", "Insurance Number", "Company Name", "Claim Number", "Date")
ins_tree = ttk.Treeview(ins_tab, columns=ins_columns, show="headings")
for col in ins_columns:
    ins_tree.heading(col, text=col)
    ins_tree.column(col, width=100, anchor=tk.CENTER)
ins_tree.pack(fill=tk.BOTH, expand=True)

# -------------------- Run the Application --------------------
root.mainloop()