import tkinter as tk
from tkinter import messagebox
from database import start_db, register_user, verify_user

class LoginWindow:
    # Initializes the login window, database, and elements of GUI
    def __init__(self, on_success_callback):
        self.on_success_callback = on_success_callback
        
        # Start the user database
        start_db()
        
        self.root = tk.Tk()
        self.root.title("Robot GUI Login")
        self.root.geometry("300x250")
        
        tk.Label(self.root, text="Username").pack(pady=(20, 5))
        self.user_entry = tk.Entry(self.root)
        self.user_entry.pack(pady=5)
        
        tk.Label(self.root, text="Password").pack(pady=5)
        self.pass_entry = tk.Entry(self.root, show="*")
        self.pass_entry.pack(pady=5)
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Login", command=self.handle_login).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Register", command=self.handle_register).pack(side="left", padx=5)
        
    # Handles login authentication and triggers success callback
    def handle_login(self):
        user = self.user_entry.get()
        pwd = self.pass_entry.get()
        
        if verify_user(user, pwd):
            messagebox.showinfo("Success", "Login successful.")
            self.root.destroy()
            self.on_success_callback()
        else:
            messagebox.showerror("Error", "Invalid username or password.")
            
    # Handles new user registration and validates user's input
    def handle_register(self):
        user = self.user_entry.get()
        pwd = self.pass_entry.get()
        
        if not user or not pwd:
            messagebox.showerror("Error", "Please enter both a username and password.")
            return
            
        if register_user(user, pwd):
            messagebox.showinfo("Success", "User successfully registered.")
        else:
            messagebox.showerror("Error", "Username already exists.")
            
    # Starts the tkinter main loop
    def run(self):
        self.root.mainloop()
