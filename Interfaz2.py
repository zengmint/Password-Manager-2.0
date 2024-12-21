import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

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

def import_csv():
    """Import data from a CSV file into the database."""
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
                    query = load_query("INSERT_ACCOUNT")
                    cursor.execute(query, (cuenta, usuario, contraseña))
                except sqlite3.IntegrityError:
                    pass  # Skip duplicate entries

        conn.commit()
        conn.close()
        messagebox.showinfo("Import Successful", "Data imported successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Initialize Database
def initialize_db():
    conn = sqlite3.connect("initdb.db")
    cursor = conn.cursor()
    create_table_query = load_query("CREATE_TABLE")
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

# Fetch all accounts using pandas
def get_all_accounts():
    conn = sqlite3.connect("initdb.db")
    query = load_query("SELECT_ALL_ACCOUNTS")
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df["cuenta"].tolist()

# Fetch account details using pandas
def get_account_details(account):
    conn = sqlite3.connect("initdb.db")
    query = load_query("SELECT_ACCOUNT_DETAILS")
    df = pd.read_sql_query(query, conn, params=(account,))
    conn.close()
    if not df.empty:
        return df.iloc[0]["usuario"], df.iloc[0]["contraseña"]
    return None, None

# Update account details using pandas
def update_account(account, new_username, new_password):
    conn = sqlite3.connect("initdb.db")
    cursor = conn.cursor()
    query = load_query("UPDATE_ACCOUNT")
    cursor.execute(query, (new_username, new_password, account))
    conn.commit()
    conn.close()

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

        conn = sqlite3.connect("initdb.db")
        cursor = conn.cursor()
        try:
            query = load_query("INSERT_ACCOUNT")
            cursor.execute(query, (account, username, password))
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
        def authenticate():
            entered_password = password_prompt.get()
            if entered_password == "cambio":
                new_username = username_var.get()
                new_password = password_var.get()

                if not new_username or not new_password:
                    messagebox.showwarning("Warning", "All fields are required!")
                    return

                selected_account = account_combo.get()
                update_account(selected_account, new_username, new_password)

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

if __name__ == "__main__":
    initialize_db()
    main_menu()

