import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

def initialize_db():
    """ Crea la tabla 'cuentas' en la base de datos 'initdb.db' si no existe. """
    try:
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
    except Exception as e:
        print(f"Error initializing database: {e}")

def import_csv():
    """ Importa datos de un archivo CSV a la base de datos. """
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
                    # Ignorar líneas duplicadas
                    pass

        conn.commit()
        conn.close()
        messagebox.showinfo("Import Successful", "Data imported successfully!")  # Added closing parenthesis
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Main Window
def main_menu():
    root = tk.Tk()
    root.title("Password Manager 2.0")
    root.geometry("350x500")
    root.configure(bg="#f4f4f4")

    # Welcome Label
    welcome_label = tk.Label(root, text="Welcome to Password Manager 2.0", font=("Arial", 16), bg="#f4f4f4")
    welcome_label.pack(pady=20)

    # Button Icons
    add_icon = ImageTk.PhotoImage(Image.open("add_icon.png").resize((50, 50)))
    consult_icon = ImageTk.PhotoImage(Image.open("consult_icon.png").resize((50, 50)))
    modify_icon = ImageTk.PhotoImage(Image.open("modify_icon.png").resize((50, 50)))
    import_icon = ImageTk.PhotoImage(Image.open("import_icon.png").resize((50, 50)))

    # Buttons
    tk.Button(root, text="Add Data", image=add_icon, compound="top", command=lambda: [root.destroy(), add_data_form()]).pack(pady=10)
    tk.Button(root, text="Consult Data", image=consult_icon, compound="top", command=lambda: [root.destroy(), consult_data_form()]).pack(pady=10)
    tk.Button(root, text="Modify Data", image=modify_icon, compound="top", command=lambda: [root.destroy(), modify_data_form()]).pack(pady=10)
    tk.Button(root, text="Import CSV", image=import_icon, compound="top", command=import_csv).pack(pady=10)

    root.mainloop()

# Add Data Form
def add_data_form():
    form = tk.Tk()
    form.title("Add Data")
    form.geometry("350x500")

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
    tk.Button(form, text="Back", command=lambda: [form.destroy(), main_menu()]).pack(pady=10)

    form.mainloop()

# Consult Data Form
def consult_data_form():
    form = tk.Tk()
    form.title("Consult Data")
    form.geometry("350x500")

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
    password_entry = tk.Entry(form, textvariable=password_var, state="disabled", show="*")
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

    def toggle_password():
        def authenticate():
            entered_password = password_prompt.get()
            if entered_password == "ver":
                password_entry.config(state="normal")
                password_window.destroy()
            else:
                messagebox.showerror("Error", "Incorrect password")
                password_window.destroy()

        password_window = tk.Toplevel(form)
        password_window.title("Authentication")
        tk.Label(password_window, text="Enter Password").pack(pady=5)
        password_prompt = tk.Entry(password_window, show="*")
        password_prompt.pack(pady=5)
        tk.Button(password_window, text="Submit", command=authenticate).pack(pady=5)

    tk.Button(form, text="Consult", command=consult_account).pack(pady=10)
    tk.Button(form, text="Show", command=toggle_password).pack(pady=10)
    tk.Button(form, text="Back", command=lambda: [form.destroy(), main_menu()]).pack(pady=10)

    form.mainloop()

# Modify Data Form
def modify_data_form():
    form = tk.Tk()
    form.title("Modify Data")
    form.geometry("350x500")

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
        def authenticate():
            entered_password = password_prompt.get()
            if entered_password == "cambio":
                new_username = username_var.get()
                new_password = password_var.get()

                if not new_username or not new_password:
                    messagebox.showwarning("Warning", "All fields are required!")
                    return

                selected_account = account_combo.get()
                conn = sqlite3.connect("initdb.db")
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE cuentas SET usuario = ?, contraseña = ? WHERE cuenta = ?",
                    (new_username, new_password, selected_account),
                )
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Account updated successfully!")
                auth_window.destroy()
                form.destroy()
                main_menu()
            else:
                messagebox.showerror("Error", "Incorrect password")
                auth_window.destroy()

        auth_window = tk.Toplevel(form)
        auth_window.title("Authentication")
        tk.Label(auth_window, text="Enter Password").pack(pady=5)
        password_prompt = tk.Entry(auth_window, show="*")
        password_prompt.pack(pady=5)
        tk.Button(auth_window, text="Submit", command=authenticate).pack(pady=5)

    tk.Button(form, text="Load", command=load_account).pack(pady=10)
    tk.Button(form, text="Modify", command=modify_account).pack(pady=10)
    tk.Button(form, text="Back", command=lambda: [form.destroy(), main_menu()]).pack(pady=10)

    form.mainloop()

# Start the application
if __name__ == "__main__":
    initialize_db()
    main_menu()

