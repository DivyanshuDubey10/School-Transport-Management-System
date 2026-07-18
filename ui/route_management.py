import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class RouteManagement(ctk.CTkFrame):
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.create_widgets()
    
    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self,
            text="Add New Route",
            font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)
        
        self.route_name_label = ctk.CTkLabel(
            self,
            text="Route Name",
            font=("Arial", 16)
        )
        self.route_name_label.pack(pady=(10, 5))
        
        self.route_name_entry = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Enter Route Name"
        )
        self.route_name_entry.pack(pady=(0, 10))
        

        self.save_button = ctk.CTkButton(
            self,
            text="Save Route",
            command=self.save_route
        )
        self.save_button.pack(pady=10)
        
    def save_route(self):
        route_name = self.route_name_entry.get()
        
        if not route_name:
            messagebox.showerror("Error", "Route Name is required.")
            return
        from dal import db_dal
        
        try:
            success = db_dal.add_route(route_name)
            if success:
                messagebox.showinfo("Success", "Route saved successfully.")
                # Clear entries
                self.route_name_entry.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


