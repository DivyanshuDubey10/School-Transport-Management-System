import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class DriverManagement:
    
    def __init__(self, master=None):
        if master is None:
            self.window = ctk.CTk()
        else:
            self.window = ctk.CTkToplevel(master)
            
        self.window.title("Driver Management")
        self.window.geometry("700x500")
        self.window.resizable(False, False)
        
        self.create_widgets()
    
    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self.window,
            text="Add New Driver",
            font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)
        
        self.driver_name_label = ctk.CTkLabel(
            self.window,
            text="Driver Name",
            font=("Arial", 16)
        )
        self.driver_name_label.pack(pady=(10, 5))
        
        self.driver_name_entry = ctk.CTkEntry(
            self.window,
            width=300,
            placeholder_text="Enter Driver Name"
        )
        self.driver_name_entry.pack(pady=(0, 10))
        
        self.driver_phone_label = ctk.CTkLabel(
            self.window,
            text="Phone Number",
            font=("Arial", 16)
        )
        self.driver_phone_label.pack(pady=(10, 5))
        
        self.driver_phone_entry = ctk.CTkEntry(
            self.window,
            width=300,
            placeholder_text="Enter Phone Number"
        )
        self.driver_phone_entry.pack(pady=(0, 10))
        
        self.address_label = ctk.CTkLabel(
            self.window,
            text="Address",
            font=("Arial", 16)
        )
        self.address_label.pack(pady=(10, 5))
        
        self.address_entry = ctk.CTkEntry(
            self.window,
            width=300,
            placeholder_text="Enter Address"
        )
        self.address_entry.pack(pady=(0, 20))
        
        self.save_button = ctk.CTkButton(
            self.window,
            text="Save Driver",
            command=self.save_driver
        )
        self.save_button.pack(pady=10)
        
    def save_driver(self):
        driver_name = self.driver_name_entry.get()
        driver_phone = self.driver_phone_entry.get()
        address = self.address_entry.get()
        
        if not driver_name:
            messagebox.showerror("Error", "Driver Name is required.")
            return
        
        if not driver_phone:
            messagebox.showerror("Error", "Phone Number is required.")
            return
            
        if not address:
            messagebox.showerror("Error", "Address is required.")
            return

        connection = connect_database()
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                """ 
                INSERT INTO driver (driver_name, driver_phone, address)
                VALUES (?, ?, ?)
                """,
                (driver_name, driver_phone, address)
            )
            connection.commit()
            messagebox.showinfo("Success", "Driver saved successfully.")
            
            # Clear entries
            self.driver_name_entry.delete(0, "end")
            self.driver_phone_entry.delete(0, "end")
            self.address_entry.delete(0, "end")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            connection.close()

    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()

if __name__ == "__main__":
    app = DriverManagement()
    app.run()
