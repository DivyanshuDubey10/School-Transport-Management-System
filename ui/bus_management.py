import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class BusManagement:
    
    def __init__(self, master=None):
        if master is None:
            self.window = ctk.CTk()
        else:
            self.window = ctk.CTkToplevel(master)
            
        self.window.title("Bus Management")
        self.window.geometry("700x550")
        self.window.resizable(False, False)
        
        self.fetch_drivers()
        self.fetch_routes()
        self.create_widgets()
        
    def fetch_drivers(self):
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute("SELECT driver_name, driver_phone FROM driver")
        rows = cursor.fetchall()
        connection.close()
        
        self.drivers = {row[0]: row[1] for row in rows}
        self.driver_names = list(self.drivers.keys())
        
    def fetch_routes(self):
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute("SELECT route_id, route_name FROM route")
        self.route_options = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
        if not self.route_options: self.route_options = [""]
        connection.close()
    
    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self.window,
            text="Add New Bus",
            font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)
        
        # Bus Number
        self.bus_number_label = ctk.CTkLabel(
            self.window,
            text="Bus Number",
            font=("Arial", 16)
        )
        self.bus_number_label.pack(pady=(10, 5))
        
        self.bus_number_entry = ctk.CTkEntry(
            self.window,
            width=300,
            placeholder_text="Enter Bus Number"
        )
        self.bus_number_entry.pack(pady=(0, 10))
        
        # Driver Name
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
        
        # Driver Phone
        self.driver_phone_label = ctk.CTkLabel(
            self.window,
            text="Driver Phone",
            font=("Arial", 16)
        )
        self.driver_phone_label.pack(pady=(10, 5))
        
        self.driver_phone_entry = ctk.CTkEntry(
            self.window,
            width=300,
            placeholder_text="Enter Driver Phone"
        )
        self.driver_phone_entry.pack(pady=(0, 10))
        
        # Capacity
        self.capacity_label = ctk.CTkLabel(
            self.window,
            text="Capacity",
            font=("Arial", 16)
        )
        self.capacity_label.pack(pady=(10, 5))
        
        self.capacity_entry = ctk.CTkEntry(
            self.window,
            width=300,
            placeholder_text="Enter Bus Capacity"
        )
        self.capacity_entry.pack(pady=(0, 10))
        
        # Route Assignment
        self.route_label = ctk.CTkLabel(
            self.window,
            text="Assign Route",
            font=("Arial", 16)
        )
        self.route_label.pack(pady=(10, 5))
        
        self.route_dropdown = ctk.CTkComboBox(
            self.window, width=300, values=self.route_options
        )
        self.route_dropdown.pack(pady=(0, 20))
        self.route_dropdown.set("Select Route" if not self.route_options[0] == "" else "No Routes Available")
        
        # Save Button
        self.save_button = ctk.CTkButton(
            self.window,
            text="Save Bus",
            command=self.save_bus
        )
        self.save_button.pack(pady=10)
        

    def save_bus(self):
        bus_number = self.bus_number_entry.get()
        driver_name = self.driver_name_entry.get()
        driver_phone = self.driver_phone_entry.get()
        capacity = self.capacity_entry.get()
        route_selection = self.route_dropdown.get()
        route_id = route_selection.split(" - ")[0] if " - " in route_selection else ""
        
        if not bus_number:
            messagebox.showerror("Error", "Bus Number is required.")
            return
            
        if not driver_name:
            messagebox.showerror("Error", "Driver Name is required.")
            return
            
        if not driver_phone:
            messagebox.showerror("Error", "Driver Phone is required.")
            return
            
        if not capacity:
            messagebox.showerror("Error", "Capacity is required.")
            return
            
        try:
            capacity = int(capacity)
        except ValueError:
            messagebox.showerror("Error", "Capacity must be a valid number.")
            return

        connection = connect_database()
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                """ 
                INSERT INTO bus (bus_number, driver_name, driver_phone, capacity, route_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (bus_number, driver_name, driver_phone, capacity, route_id if route_id else None)
            )
            connection.commit()
            messagebox.showinfo("Success", "Bus saved successfully.")
            
            # Clear entries
            self.bus_number_entry.delete(0, "end")
            self.driver_name_entry.delete(0, "end")
            self.driver_phone_entry.delete(0, "end")
            self.capacity_entry.delete(0, "end")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            connection.close()

    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()

if __name__ == "__main__":
    app = BusManagement()
    app.run()
