import customtkinter as ctk
from tkinter import messagebox
from database import connect_database
from ui.admin_dashboard import AdminDashboard
from ui.parent_dashboard import ParentDashboard


class LoginWindow:

    def __init__(self, master=None):
        if master is None:
            self.window = ctk.CTk()
        else:
            self.window = ctk.CTkToplevel(master)

        self.window.title("School Transport Management System")
        self.window.geometry("900x600")
        self.window.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):

        # Login Frame
        self.login_frame = ctk.CTkFrame(self.window, width=500, height=400)

        self.login_frame.pack(expand=True)

        # Title
        self.title_label = ctk.CTkLabel(
            self.login_frame,
            text="School Transport Management System",
            font=("Arial", 28, "bold"),
        )

        self.title_label.pack(pady=(30, 25))

        # Username Label
        self.username_label = ctk.CTkLabel(
            self.login_frame, text="Username", font=("Arial", 16)
        )

        self.username_label.pack(pady=(10, 5))

        # Username Entry
        self.username_entry = ctk.CTkEntry(self.login_frame, width=300)

        self.username_entry.pack(pady=(0, 20))

        # Password label
        self.password_label = ctk.CTkLabel(
            self.login_frame, text="Password", font=("Arial", 16)
        )
        self.password_label.pack(pady=(10, 5))

        # Password Entry
        self.password_entry = ctk.CTkEntry(self.login_frame, width=300, show="*")
        self.password_entry.pack(pady=(0, 20))

        self.show_password = ctk.BooleanVar()

        # Show password checkbox
        self.password_entry_checkbox = ctk.CTkCheckBox(
            self.login_frame,
            text="Show Password",
            variable=self.show_password,
            command=self.toggle_password_visibility,
        )

        self.password_entry_checkbox.pack(pady=(0, 20))

        # Login Button
        self.login_button = ctk.CTkButton(
            self.login_frame, text="Login", command=self.login
        )
        self.login_button.pack(pady=(10, 20))

    def toggle_password_visibility(self):
        if self.show_password.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def login(self):

        username = self.username_entry.get()
        password = self.password_entry.get()

        connection = connect_database()
        cursor = connection.cursor()
        
        # Check Admin first
        cursor.execute(
            "SELECT * FROM admin WHERE USERNAME = ? AND password = ?",
            (username, password)
        )
        admin = cursor.fetchone()
        if admin:
           messagebox.showinfo("Success", "Login Successful as Admin!")
           if isinstance(self.window, ctk.CTk):
               self.window.withdraw()
           else:
               self.window.destroy()
           dashboard = AdminDashboard(master=self.window.master if isinstance(self.window, ctk.CTkToplevel) else self.window)
           dashboard.run()
           return

        # Check Parent
        cursor.execute(
            "SELECT * FROM parent WHERE username = ? AND password = ?",
            (username, password)
        )
        parent = cursor.fetchone()
        if parent:
           messagebox.showinfo("Success", f"Welcome back, {parent[1]}!")
           if isinstance(self.window, ctk.CTk):
               self.window.withdraw()
           else:
               self.window.destroy()
           parent_id = parent[0]
           dashboard = ParentDashboard(parent_id, master=self.window.master if isinstance(self.window, ctk.CTkToplevel) else self.window)
           dashboard.run()
           return
           
        messagebox.showerror("Error", "Invalid username or password.")

    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()
