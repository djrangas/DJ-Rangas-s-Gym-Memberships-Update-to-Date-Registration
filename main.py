import tkinter as tk
from tkinter import messagebox

def open_main_program():
    print("Hello, world!")

def authenticate():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "root":
        login_window.destroy()
        open_main_program()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("400x200")

tk.Label(login_window, text="Username:").pack(pady=10)
username_entry = tk.Entry(login_window)
username_entry.pack()

tk.Label(login_window, text="Password:").pack(pady=10)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack()

login_button = tk.Button(login_window, text="Login", command=authenticate)
login_button.pack(pady=10)

login_window.mainloop()