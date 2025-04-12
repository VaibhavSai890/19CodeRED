import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def parse_record(record):
    rec = {}
    lines = record.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    
    if lines and "MEDI-SURE HOSPITAL" in lines[0]:
        lines.pop(0)
    
    if lines:
        category_line = lines.pop(0)
        rec['Category'] = category_line.upper()
    else:
        rec['Category'] = "UNKNOWN"
    
    for line in lines:
        if ':' in line:
            parts = line.split(":", 1)
        elif '-' in line:
            parts = line.split("-", 1)
        else:
            continue
        key = parts[0].strip()
        value = parts[1].strip()
        rec[key] = value
    return rec

def process_file_content(content):
    employee_records = []
    pharma_records = []
    insurance_records = []

    raw_records = content.split('--- Page 1 ---')
    for raw in raw_records:
        raw = raw.strip()
        if not raw:
            continue
        record = parse_record(raw)
        cat = record.get('Category', '')
        if "INSURANCE BILL" in cat:
            insurance_records.append(record)
        elif "EMPLOYEE BILL" in cat:
            employee_records.append(record)
        elif "PHARMACETICAL" in cat or "EQUIPMENTS" in cat:
            pharma_records.append(record)
    return employee_records, pharma_records, insurance_records

def load_file():
    filepath = filedialog.askopenfilename(title="Select a Text File", filetypes=[("Text Files", "*.txt")])
    if filepath:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            global emp_records, pharma_records, ins_records
            emp_records, pharma_records, ins_records = process_file_content(content)

            # Save parsed output to a text file
            with open("parsed_output.txt", "w", encoding='utf-8') as f:
                f.write("EMPLOYEE RECORDS:\n")
                for rec in emp_records:
                    f.write(str(rec) + "\n")
                f.write("\nPHARMACEUTICAL RECORDS:\n")
                for rec in pharma_records:
                    f.write(str(rec) + "\n")
                f.write("\nINSURANCE RECORDS:\n")
                for rec in ins_records:
                    f.write(str(rec) + "\n")

            messagebox.showinfo("Success", "File loaded and processed successfully!")
            display_tables()
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file:\n{e}")

def clear_tree(tree):
    for item in tree.get_children():
        tree.delete(item)

def display_tables():
    clear_tree(emp_tree)
    clear_tree(pharma_tree)
    clear_tree(ins_tree)
    
    for rec in emp_records:
        values = (
            rec.get("Name", ""),
            rec.get("Address", ""),
            rec.get("Phone No", ""),
            rec.get("Employee ID", ""),
            rec.get("Post", ""),
            
            rec.get("Salary", "") if "Salary" in rec else rec.get("Salary - Tax", ""),
            rec.get("Hours Worked", "")
        )
        emp_tree.insert("", tk.END, values=values)
        
    for rec in pharma_records:
        values = (
            rec.get("Name", ""),
            rec.get("Addres s", "") or rec.get("Address", ""),
            rec.get("Phone No", ""),
            rec.get("Invoice No", ""),
            rec.get("Vendor Name", ""),
            rec.get("Vendor Address", ""),
            rec.get("Date", ""),
            rec.get("Items", ""),
            rec.get("Quantity", ""),
            rec.get("Cost", "") or rec.get("Cost+Tax", "")
        )
        pharma_tree.insert("", tk.END, values=values)
    
    for rec in ins_records:
        values = (
            rec.get("Name", ""),
            rec.get("Addres s", "") or rec.get("Address", ""),
            rec.get("Phone No", ""),
            rec.get("Insurance number", ""),
            rec.get("Company name", ""),
            rec.get("Claim Number", ""),
            rec.get("Date", "")
        )
        ins_tree.insert("", tk.END, values=values)

# -------------------- GUI Setup --------------------

root = tk.Tk()
root.title("Jumbled Data Arranger")

emp_records = []
pharma_records = []
ins_records = []

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

load_btn = tk.Button(top_frame, text="Load Text File", command=load_file)
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