from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# Database connection
DATABASE_URL = "sqlite:///initdb.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, execution_options={"future_result": True})
Session = sessionmaker(bind=engine)

# SQL Queries
CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS cuentas (
    cuenta TEXT PRIMARY KEY,
    usuario TEXT NOT NULL,
    contrasena TEXT NOT NULL
);
"""

INSERT_ACCOUNT = """
INSERT INTO cuentas (cuenta, usuario, contrasena) VALUES (:cuenta, :usuario, :contrasena);
"""

SELECT_ALL_ACCOUNTS = """
SELECT cuenta FROM cuentas;
"""

SELECT_ACCOUNT_DETAILS = """
SELECT usuario, contrasena FROM cuentas WHERE cuenta = :account;
"""

UPDATE_ACCOUNT = """
UPDATE cuentas SET usuario = :new_username, contrasena = :new_password WHERE cuenta = :account;
"""

# Initialize Database
def initialize_db():
    with engine.connect() as connection:
        connection.execute(text(CREATE_TABLE))

# Import data from CSV
def import_csv():
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    if not file_path:
        return

    try:
        with engine.connect() as connection:
            with open(file_path, "r") as file:
                for line in file:
                    cuenta, usuario, contrasena = line.strip().split(",")
                    try:
                        connection.execute(text(INSERT_ACCOUNT), {
                            "cuenta": cuenta,
                            "usuario": usuario,
                            "contrasena": contrasena
                        })
                    except Exception:
                        pass  # Skip duplicate entries
        messagebox.showinfo("Import Successful", "Data imported successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Fetch all accounts
def get_all_accounts():
    with engine.connect() as connection:
        result = connection.execute(text(SELECT_ALL_ACCOUNTS)).fetchall()
        return [row[0] for row in result]

# Fetch account details
def get_account_details(account):
    with engine.connect() as connection:
        result = connection.execute(text(SELECT_ACCOUNT_DETAILS), {"account": account}).fetchone()
        if result:
            # Accessing tuple results by index
            return result[0], result[1]  # usuario, contrasena
        return None, None

# Update account details
def update_account(account, new_username, new_password):
    with engine.connect() as connection:
        connection.execute(
            text(UPDATE_ACCOUNT),
            {
                "new_username": new_username,
                "new_password": new_password,
                "account": account
            }
        )
        connection.commit()  # Explicit commit after update

# Main Window
def main_menu():
    root = tk.Tk()
    root.title("Password Manager 2.0")
    root.geometry("350x500+500+200")  # Fixed position
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

# Modify Data Form
def modify_data_form():
    form = tk.Tk()
    form.title("Modify Data")
    form.geometry("350x500+500+200")

    tk.Label(form, text="Modify Account Data", font=("Arial", 14)).pack(pady=10)

    accounts = get_all_accounts()

    tk.Label(form, text="Select Account").pack()
    account_combo = ttk.Combobox(form, values=accounts, state="readonly")
    account_combo.pack(pady=5)

    username_var = tk.StringVar()
    password_var = tk.StringVar()

    tk.Label(form, text="Username").pack()
    username_entry = tk.Entry(form, textvariable=username_var)
    username_entry.pack(pady=5)

    tk.Label(form, text="Password").pack()
    password_entry = tk.Entry(form, textvariable=password_var, show="*")
    password_entry.pack(pady=5)

    def load_account():
        selected_account = account_combo.get()
        if not selected_account:
            messagebox.showwarning("Warning", "Please select an account!")
            return

        username, password = get_account_details(selected_account)

        if username and password:
            username_var.set(username)
            password_var.set(password)
        else:
            messagebox.showerror("Error", "Account not found!")

    def modify_account():
        # Password verification
        def verify_password():
            entered_password = password_prompt.get()
            if entered_password == "cambio":  # Check if password is correct
                new_username = username_var.get()
                new_password = password_var.get()

                if not new_username or not new_password:
                    messagebox.showwarning("Warning", "All fields are required!")
                    return

                selected_account = account_combo.get()
                try:
                    update_account(selected_account, new_username, new_password)
                    messagebox.showinfo("Success", "Account updated successfully!")
                    form.destroy()
                    main_menu()  # Reload main menu
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                password_window.destroy()

            else:
                messagebox.showerror("Error", "Incorrect password")
                password_window.destroy()

        password_window = tk.Toplevel(form)
        password_window.title("Enter Password")
        password_window.geometry("300x150")

        tk.Label(password_window, text="Enter the password to modify account").pack(pady=10)
        password_prompt = tk.Entry(password_window, show="*")
        password_prompt.pack(pady=5)
        tk.Button(password_window, text="Authenticate", command=verify_password).pack(pady=10)

    tk.Button(form, text="Load Account", command=load_account).pack(pady=10)
    tk.Button(form, text="Modify", command=modify_account).pack(pady=10)
    tk.Button(form, text="Back", command=lambda: [form.destroy(), main_menu()]).pack(pady=10)

    form.mainloop()

# Consult Data Form
def consult_data_form():
    form = tk.Tk()
    form.title("Consult Data")
    form.geometry("350x500+500+200")  # Fixed position

    tk.Label(form, text="Consult Account Data", font=("Arial", 14)).pack(pady=10)

    accounts = get_all_accounts()

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

        # Fetch updated account details
        username, password = get_account_details(selected_account)

        if username and password:
            username_var.set(username)
            password_var.set(password)
        else:
            messagebox.showerror("Error", "Account not found!")

    def toggle_password():
        def authenticate():
            entered_password = password_prompt.get()
            if entered_password == "ver":
                password_entry.config(show="")  # Display the actual password
                password_window.destroy()
            else:
                messagebox.showerror("Error", "Incorrect password")
                password_window.destroy()

        password_window = tk.Toplevel(form)
        password_window.title("Enter Password")
        password_window.geometry("300x150")

        tk.Label(password_window, text="Enter the password to view account").pack(pady=10)
        password_prompt = tk.Entry(password_window, show="*")
        password_prompt.pack(pady=5)
        tk.Button(password_window, text="Authenticate", command=authenticate).pack(pady=10)

    tk.Button(form, text="Consult", command=consult_account).pack(pady=10)
    tk.Button(form, text="View Password", command=toggle_password).pack(pady=10)
    tk.Button(form, text="Back", command=lambda: [form.destroy(), main_menu()]).pack(pady=10)

    form.mainloop()

if __name__ == "__main__":
    initialize_db()
    main_menu()
