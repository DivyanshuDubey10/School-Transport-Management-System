import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from database import connect_database

class ParentManagement(ctk.CTkFrame):
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.create_widgets()
    
    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self,
            text="Parent Management",
            font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)
        
        self.parent_name = ctk.CTkLabel(
            self,
            text = "Parent Name",
            font = ("Arial", 16)
        )
        self.parent_name.pack(pady=10)
        
        self.parent_name_entry = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Enter Parent Name"
        )
        self.parent_name_entry.pack(pady=10)
        
        self.username_label = ctk.CTkLabel(
            self,
            text="Username",
        )
        self.username_label.pack()
        
        self.username_entry = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Enter Username"
        )
        self.username_entry.pack(pady=10)
        
        self.password_label = ctk.CTkLabel(
            self,
            text="Password"
        )
        self.password_label.pack()
        
        self.password_entry = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Enter Password",
            show="*"
        )
        self.password_entry.pack(pady=10)
        
        self.phone_label = ctk.CTkLabel(
            self,
            text="Phone Number"
        )
        self.phone_label.pack()

        self.phone_entry = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Enter Phone Number"
        )
        self.phone_entry.pack(pady=10)
        
        self.address_label = ctk.CTkLabel(
            self,
            text="Address"
        )
        self.address_label.pack()

        self.address_entry = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Enter Address"
        )
        self.address_entry.pack(pady=10)
        
        self.pickup_label = ctk.CTkLabel(
            self,
            text="Pickup Point"
        )
        self.pickup_label.pack()

        self.pickup_entry = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Enter Pickup Point"
        )
        self.pickup_entry.pack(pady=10)
        
        self.save_button = ctk.CTkButton(
            self,
            text="Save Parent",
            command=self.save_parent
        )
        self.save_button.pack(pady=20)
        
    def save_parent(self):
        parent_name = self.parent_name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()
        pickup_point = self.pickup_entry.get()
        
        if not parent_name:
            messagebox.showerror("Error", "Parent Name is required.")
            return
        
        if not username:
            messagebox.showerror("Error", "Username is required.")
            return
        
        if not password:
            messagebox.showerror("Password", "Password is required.")
            return

        if not phone:
            messagebox.showerror("Error", "Phone Number is required.")
            return

        if not address:
            messagebox.showerror("Error", "Address is required.")
            return
            
        if not pickup_point:
            messagebox.showerror("Error", "Pickup Point is required.")
            return
            
        from dal import db_dal
        
        try:
            success = db_dal.add_parent(parent_name, phone, address, pickup_point, username, password)
            if success:
                messagebox.showinfo(
                     "Success", "Parent information saved successfully."
                )
                
                self.parent_name_entry.delete(0, 'end')
                self.username_entry.delete(0, 'end')
                self.password_entry.delete(0, 'end')
                self.phone_entry.delete(0, 'end')
                self.address_entry.delete(0, 'end')
                self.pickup_entry.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
