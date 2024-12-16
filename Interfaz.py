import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog

# Database initialization
def initialize_database():
    conn = sqlite3.connect("initdb.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cuentas (
            cuenta VARCHAR(30) PRIMARY KEY,
            usuario VARCHAR(30),
            contraseña VARCHAR(30)
        )
    ''')
    conn.commit()
    conn.close()

# Add data to the database
def add_data(cuenta, usuario, contraseña):
    try:
        conn = sqlite3.connect("initdb.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cuentas (cuenta, usuario, contraseña) VALUES (?, ?, ?)", (cuenta, usuario, contraseña))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Data added successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Account already exists!")

# Fetch data for a specific account
def fetch_data(cuenta):
    conn = sqlite3.connect("initdb.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cuentas WHERE cuenta = ?", (cuenta,))
    result = cursor.fetchone()
    conn.close()
    return result

# Fetch all account names
def fetch_all_accounts():
    conn = sqlite3.connect("initdb.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cuenta FROM cuentas")
    results = cursor.fetchall()
    conn.close()
    return [row[0] for row in results]

# Update data for a specific account
def update_data(cuenta, usuario, contraseña):
    conn = sqlite3.connect("initdb.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE cuentas SET usuario = ?, contraseña = ? WHERE cuenta = ?", (usuario, contraseña, cuenta))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Data updated successfully!")

# GUI components
def main_menu():
    def open_add_form():
        menu.destroy()
        add_form()

    def open_fetch_form():
        menu.destroy()
        fetch_form()

    def open_update_form():
        menu.destroy()
        update_form()

    menu = tk.Tk()
    menu.title("Main Menu")
    tk.Button(menu, text="Add Data", command=open_add_form).pack(pady=10)
    tk.Button(menu, text="Consult Data", command=open_fetch_form).pack(pady=10)
    tk.Button(menu, text="Modify Data", command=open_update_form).pack(pady=10)
    menu.mainloop()

def add_form():
    def toggle_password():
        if contraseña_entry.cget('show') == '*':
            contraseña_entry.config(show='')
        else:
            contraseña_entry.config(show='*')

    def submit():
        cuenta = cuenta_entry.get()
        usuario = usuario_entry.get()
        contraseña = contraseña_entry.get()
        add_data(cuenta, usuario, contraseña)
        add.destroy()
        main_menu()

    add = tk.Tk()
    add.title("Add Data")

    tk.Label(add, text="Account:").pack()
    cuenta_entry = tk.Entry(add)
    cuenta_entry.pack()

    tk.Label(add, text="User:").pack()
    usuario_entry = tk.Entry(add)
    usuario_entry.pack()

    tk.Label(add, text="Password:").pack()
    contraseña_entry = tk.Entry(add, show="*")
    contraseña_entry.pack()

    tk.Button(add, text="Toggle Password", command=toggle_password).pack(pady=5)
    tk.Button(add, text="Submit", command=submit).pack(pady=10)

    add.mainloop()

def fetch_form():
    def consult():
        cuenta = cuenta_var.get()
        data = fetch_data(cuenta)
        if data:
            usuario_entry.config(state=tk.NORMAL)
            contraseña_entry.config(state=tk.NORMAL)
            usuario_entry.delete(0, tk.END)
            contraseña_entry.delete(0, tk.END)
            usuario_entry.insert(0, data[1])
            contraseña_entry.insert(0, data[2])
            usuario_entry.config(state=tk.DISABLED)
            contraseña_entry.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Error", "Account not found!")

    def toggle_password():
        if contraseña_entry.cget('show') == '*':
            contraseña_entry.config(show='')
        else:
            contraseña_entry.config(show='*')

    fetch = tk.Tk()
    fetch.title("Consult Data")

    tk.Label(fetch, text="Select Account:").pack()
    cuenta_var = tk.StringVar(fetch)
    cuentas = fetch_all_accounts()
    if cuentas:
        cuenta_var.set(cuentas[0])  # Set default value
    cuenta_menu = tk.OptionMenu(fetch, cuenta_var, *cuentas)
    cuenta_menu.pack()

    tk.Button(fetch, text="Consult", command=consult).pack(pady=10)

    tk.Label(fetch, text="User:").pack()
    usuario_entry = tk.Entry(fetch, state=tk.DISABLED)
    usuario_entry.pack()

    tk.Label(fetch, text="Password:").pack()
    contraseña_entry = tk.Entry(fetch, show="*", state=tk.DISABLED)
    contraseña_entry.pack()

    tk.Button(fetch, text="Show", command=toggle_password).pack(pady=5)
    tk.Button(fetch, text="Back", command=lambda: [fetch.destroy(), main_menu()]).pack(pady=5)

    fetch.mainloop()

def update_form():
    def search():
        cuenta = cuenta_entry.get()
        data = fetch_data(cuenta)
        if data:
            usuario_entry.delete(0, tk.END)
            contraseña_entry.delete(0, tk.END)
            usuario_entry.insert(0, data[1])
            contraseña_entry.insert(0, data[2])
        else:
            messagebox.showerror("Error", "Account not found!")

    def modify():
        auth_password = simpledialog.askstring("Authentication", "Enter password to confirm modification:", show='*')
        if auth_password == "cambio":
            cuenta = cuenta_entry.get()
            usuario = usuario_entry.get()
            contraseña = contraseña_entry.get()
            update_data(cuenta, usuario, contraseña)
            update.destroy()
            main_menu()
        else:
            messagebox.showerror("Error", "Incorrect password!")

    update = tk.Tk()
    update.title("Modify Data")

    tk.Label(update, text="Enter Account:").pack()
    cuenta_entry = tk.Entry(update)
    cuenta_entry.pack()

    tk.Button(update, text="Search", command=search).pack(pady=10)

    tk.Label(update, text="New User:").pack()
    usuario_entry = tk.Entry(update)
    usuario_entry.pack()

    tk.Label(update, text="New Password:").pack()
    contraseña_entry = tk.Entry(update, show="*")
    contraseña_entry.pack()

    tk.Button(update, text="Modify", command=modify).pack(pady=10)

    tk.Button(update, text="Back", command=lambda: [update.destroy(), main_menu()]).pack(pady=5)

    update.mainloop()


# Initialize database and run the main menu
initialize_database()
main_menu()
