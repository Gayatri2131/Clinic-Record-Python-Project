import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Database Connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # change to your MySQL username
        password="Us_21290331",  # change to your MySQL password
        database="clinic3",
        use_pure=True
    )


# ---------------- GUI START ----------------
root = tk.Tk()
root.title("Clinic Patient Records - MySQL")
root.geometry("900x600")


# Variables
name_var = tk.StringVar()
age_var = tk.StringVar()
gender_var = tk.StringVar()
diagnosis_var = tk.StringVar()


# ---- Form Frame ----
form_frame = tk.LabelFrame(root, text="Patient Details", padx=10, pady=10)
form_frame.pack(fill="x", padx=10, pady=5)

tk.Label(form_frame, text="Name").grid(row=0, column=0)
tk.Entry(form_frame, textvariable=name_var).grid(row=0, column=1)

tk.Label(form_frame, text="Age").grid(row=0, column=2)
tk.Entry(form_frame, textvariable=age_var).grid(row=0, column=3)

tk.Label(form_frame, text="Gender").grid(row=1, column=0)
tk.Entry(form_frame, textvariable=gender_var).grid(row=1, column=1)

tk.Label(form_frame, text="Diagnosis").grid(row=1, column=2)
tk.Entry(form_frame, textvariable=diagnosis_var).grid(row=1, column=3)


# ---- Table Frame ----
table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("id", "name", "age", "gender", "diagnosis")
patient_table = ttk.Treeview(table_frame, columns=columns, show="headings")

for col in columns:
    patient_table.heading(col, text=col.capitalize())
    patient_table.column(col, width=120)

patient_table.pack(fill="both", expand=True)


# ---- Functions ----
def clear_fields():
    name_var.set("")
    age_var.set("")
    gender_var.set("")
    diagnosis_var.set("")

def fetch_patients():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    conn.close()

    # Clear old data in Treeview
    for row in patient_table.get_children():
        patient_table.delete(row)

    # Insert new data into Treeview
    for row in rows:
        patient_table.insert("", "end", values=row)

    # ---- Print in IDLE console ----
    print("\nPatient Records:")
    for row in rows:
        print(row)

def add_patient():
    if not name_var.get() or not age_var.get() or not gender_var.get():
        messagebox.showerror("Error", "Please fill all required fields")
        return
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO patients (name, age, gender, diagnosis) VALUES (%s, %s, %s, %s)",
        (name_var.get(), age_var.get(), gender_var.get(), diagnosis_var.get())
    )
    conn.commit()
    conn.close()
    fetch_patients()
    clear_fields()


def show_statistics():
    conn = connect_db()
    cursor = conn.cursor()

    # Total Patients
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    # Gender Distribution
    cursor.execute("SELECT gender, COUNT(*) FROM patients GROUP BY gender")
    gender_data = cursor.fetchall()
    genders = [row[0] for row in gender_data]
    gender_counts = [row[1] for row in gender_data]

    # Top Diagnoses
    cursor.execute("SELECT diagnosis, COUNT(*) FROM patients GROUP BY diagnosis ORDER BY COUNT(*) DESC LIMIT 5")
    diagnosis_data = cursor.fetchall()
    diagnoses = [row[0] for row in diagnosis_data]
    diagnosis_counts = [row[1] for row in diagnosis_data]

    conn.close()

    # Create Matplotlib Figure
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))

    axs[0].text(0.5, 0.5, f"Total Patients:\n{total_patients}", fontsize=14, ha="center", va="center")
    axs[0].axis("off")

    axs[1].pie(gender_counts, labels=genders, autopct="%1.1f%%", startangle=90)
    axs[1].set_title("Gender Distribution")

    axs[2].bar(diagnoses, diagnosis_counts, color="skyblue")
    axs[2].set_title("Top Diagnoses")
    axs[2].set_ylabel("Count")

    stats_window = tk.Toplevel(root)
    stats_window.title("Patient Statistics")

    canvas = FigureCanvasTkAgg(fig, master=stats_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# ---- Buttons ----
tk.Button(form_frame, text="Add", command=add_patient).grid(row=2, column=0, pady=5)
tk.Button(form_frame, text="Clear", command=clear_fields).grid(row=2, column=1)
tk.Button(form_frame, text="Show All", command=fetch_patients).grid(row=2, column=2)
tk.Button(form_frame, text="Statistics", command=show_statistics).grid(row=2, column=3)


# Initial load
fetch_patients()

root.mainloop()
