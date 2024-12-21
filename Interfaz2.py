from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# Database connection
DATABASE_URL = "sqlite:///initdb.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Function to load SQL queries from an external file
def load_query(query_name, file_path="queries.sql"):
    with open(file_path, "r") as f:
        queries = f.read()
    query_dict = {}
    current_key = None
    current_value = []
    for line in queries.split("\n"):
        if " = " in line:
            if current_key:
                query_dict[current_key] = " ".join(current_value).strip()
            current_key, value = line.split(" = ", 1)
            current_value = [value.strip()]
        else:
            current_value.append(line.strip())
    if current_key:
        query_dict[current_key] = " ".join(current_value).strip()
    return query_dict.get(query_name, "")

# Initialize Database
def initialize_db():
    with engine.connect() as connection:
        query = load_query("CREATE_TABLE")
        connection.execute(text(query))

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
            query = load_query("INSERT_ACCOUNT")
            with open(file_path, "r") as file:
                for line in file:
                    cuenta, usuario, contrasena = line.strip().split(",")
                    try:
                        connection.execute(text(query), {
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
        query = load_query("SELECT_ALL_ACCOUNTS")
        result = connection.execute(text(query))
        return [row["cuenta"] for row in result]

# Fetch account details
def get_account_details(account):
    with engine.connect() as connection:
        query = load_query("SELECT_ACCOUNT_DETAILS")
        result = connection.execute(text(query), {"account": account}).fetchone()
        if result:
            return result["usuario"], result["contrasena"]
        return None, None

# Update account details
def update_account(account, new_username, new_password):
    with engine.connect() as connection:
        query = load_query("UPDATE_ACCOUNT")
        connection.execute(
            text(query),
            {
                "new_username": new_username,
                "new_password": new_password,
                "account": account
            }
        )

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

# Add Data Form
def add_data_form():
    form = tk.Tk()
    form.title("Add Data")
    form.geometry("350x500+500+200")  # Fixed position

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

        try:
            with engine.connect() as connection:
                query = load_query("INSERT_ACCOUNT")
                connection.execute(text(query), {
                    "cuenta": account,
                    "usuario": username,
                    "contrasena": password
                })
            messagebox.showinfo("Success", "Account added successfully!")
            form.destroy()
            main_menu()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    tk.Button(form, text="Add", command=add_account).pack(pady=10)
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

        username, password = get_account_details(selected_account)

        if username and password:
            username_var.set(username)
            password_var.set(password)
        else:
            messagebox.showerror("Error", "Account not found!")

    tk.Button(form, text="Consult", command=consult_account).pack(pady=10)
    tk.Button(form, text="Back", command=lambda: [form.destroy(), main_menu()]).pack(pady=10)

    form.mainloop()

# Modify Data Form
def modify_data_form():
    form = tk.Tk()
    form.title("Modify Data")
    form.geometry("350x500+500+200")  # Fixed position

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
    password_entry = tk.Entry(form, textvariable=password_var)
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
        new_username = username_var.get()
        new_password = password_var.get()
        selected_account = account_combo.get()

        if not new_username or not new_password:
            messagebox.showwarning("Warning", "All fields are required!")
            return

        try:
            update_account(selected_account, new_username, new_password)
            messagebox.showinfo("Success", "Account updated successfully!")
            form.destroy()
            main_menu()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    tk.Button(form, text="Load", command=load_account).pack(pady=10)
    tk.Button(form, text="Modify", command=modify_account).pack(pady=10)
    tk.Button(form, text="Back", command=lambda: [form.destroy(), main_menu()]).pack(pady=10)

    form.mainloop()

if __name__ == "__main__":
    initialize_db()
    main_menu()
