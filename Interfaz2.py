import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Database Setup
def initialize_db():
    conn = sqlite3.connect("initdb.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cuentas (
            cuenta TEXT PRIMARY KEY,
            usuario TEXT NOT NULL,
            contraseña TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

initialize_db()

# Functions
def import_csv():
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    if not file_path:
        return

    try:
        conn = sqlite3.connect("initdb.db")
        cursor = conn.cursor()

        with open(file_path, "r") as file:
            for line in file:
                cuenta, usuario, contraseña = line.strip().split(",")
                try:
                    cursor.execute(
                        "INSERT INTO cuentas (cuenta, usuario, contraseña) VALUES (?, ?, ?)",
                        (cuenta, usuario, contraseña),
                    )
                except sqlite3.IntegrityError:
                    continue

        conn.commit()
        conn.close()
        messagebox.showinfo("Import Successful", "Data imported successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Main Window
def main_menu():
    root = tk.Tk()
    root.title("Password Manager 2.0")
    root.geometry("600x400")
    root.configure(bg="#f4f4f4")

    # Menu Bar
    menu_bar = tk.Menu(root)

    # File Menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Import CSV", command=import_csv)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.destroy)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Navigation Menu
    nav_menu = tk.Menu(menu_bar, tearoff=0)
    nav_menu.add_command(label="Add Data", command=lambda: [root.destroy(), add_data_form()])
    nav_menu.add_command(label="Consult Data", command=lambda: [root.destroy(), consult_data_form()])
    nav_menu.add_command(label="Modify Data", command=lambda: [root.destroy(), modify_data_form()])
    menu_bar.add_cascade(label="Navigate", menu=nav_menu)

    root.config(menu=menu_bar)

    # Welcome Label
    welcome_label = tk.Label(root, text="Welcome to Password Manager 2.0", font=("Arial", 16), bg="#f4f4f4")
    welcome_label.pack(pady=20)

    root.mainloop()

# Add Data Form
def add_data_form():
    form = tk.Tk()
    form.title("Add Data")
    form.geometry("400x300")

    tk.Label(form, text="Add a New Account", font=("Arial", 14)).pack(pady=10)

    tk.Label(form, text="Account").pack()
    account_entry = tk.Entry(form)
    account_entry.pack(pady=5)

    tk.Label(form, text="Username").pack()
    username_entry = tk.Entry(form)
    username_entry.pack(pady=5)

    tk.Label(form, text="Password").pack()
    password_entry = tk.Entry(form, show="*")
    password_entry.pack(pady=5)

    def add_account():
        account = account_entry.get()
        username = username_entry.get()
        password = password_entry.get()

        if not account or not username or not password:
            messagebox.showwarning("Warning", "All fields are required!")
            return

        conn = sqlite3.connect("initdb.db")
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO cuentas (cuenta, usuario, contraseña) VALUES (?, ?, ?)",
                (account, username, password),
            )
            conn.commit()
            messagebox.showinfo("Success", "Account added successfully!")
            form.destroy()
            main_menu()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Account already exists!")
        conn.close()

    tk.Button(form, text="Add", command=add_account).pack(pady=10)

    form.mainloop()

# Consult Data Form
def consult_data_form():
    form = tk.Tk()
    form.title("Consult Data")
    form.geometry("400x300")

    tk.Label(form, text="Consult Account Data", font=("Arial", 14)).pack(pady=10)

    conn = sqlite3.connect("initdb.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cuenta FROM cuentas")
    accounts = [row[0] for row in cursor.fetchall()]
    conn.close()

    tk.Label(form, text="Select Account").pack()
    account_combo = ttk.Combobox(form, values=accounts, state="readonly")
    account_combo.pack(pady=5)

    username_var = tk.StringVar()
    password_var = tk.StringVar()

    tk.Label(form, text="Username").pack()
    username_entry = tk.Entry(form, textvariable=username_var, state="disabled")
    username_entry.pack(pady=5)

    tk.Label(form, text="Password").pack()
    password_entry = tk.Entry(form, textvariable=password_var, state="disabled")
    password_entry.pack(pady=5)

    def consult_account():
        selected_account = account_combo.get()
        if not selected_account:
            messagebox.showwarning("Warning", "Please select an account!")
            return

        conn = sqlite3.connect("initdb.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT usuario, contraseña FROM cuentas WHERE cuenta = ?", (selected_account,)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            username_var.set(result[0])
            password_var.set(result[1])
        else:
            messagebox.showerror("Error", "Account not found!")

    tk.Button(form, text="Consult", command=consult_account).pack(pady=10)

    form.mainloop()

# Modify Data Form
def modify_data_form():
    form = tk.Tk()
    form.title("Modify Data")
    form.geometry("400x400")

    tk.Label(form, text="Modify Account Data", font=("Arial", 14)).pack(pady=10)

    conn = sqlite3.connect("initdb.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cuenta FROM cuentas")
    accounts = [row[0] for row in cursor.fetchall()]
    conn.close()

    tk.Label(form, text="Select Account").pack()
    account_combo = ttk.Combobox(form, values=accounts, state="readonly")
    account_combo.pack(pady=5)

    username_var = tk.StringVar()
    password_var = tk.StringVar()

    tk.Label(form, text="Username").pack()
    username_entry = tk.Entry(form, textvariable=username_var)
    username_entry.pack(pady=5)

    tk.Label(form, text="Password").pack()
    password_entry = tk.Entry(form, textvariable=password_var)
    password_entry.pack(pady=5)

    def load_account():
        selected_account = account_combo.get()
        if not selected_account:
            messagebox.showwarning("Warning", "Please select an account!")
            return

        conn = sqlite3.connect("initdb.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT usuario, contraseña FROM cuentas WHERE cuenta = ?", (selected_account,)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            username_var.set(result[0])
            password_var.set(result[1])
        else:
            messagebox.showerror("Error", "Account not found!")

    def modify_account():
        selected_account = account_combo.get()
        new_username = username_var.get()
        new_password = password_var.get()

        if not selected_account or not new_username or not new_password:
            messagebox.showwarning("Warning", "All fields are required!")
            return

        conn = sqlite3.connect("initdb.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cuentas SET usuario = ?, contraseña = ? WHERE cuenta = ?",
            (new_username, new_password, selected_account),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Account updated successfully!")
        form.destroy()
        main_menu()

    tk.Button(form, text="Load", command=load_account).pack(pady=10)
    tk.Button(form, text="Modify", command=modify_account).pack(pady=10)

    form.mainloop()

main_menu()
