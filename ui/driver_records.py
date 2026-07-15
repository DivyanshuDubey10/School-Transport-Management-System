import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class DriverRecords:
    
    def __init__(self, master=None):
        if master is None:
            self.window = ctk.CTk()
        else:
            self.window = ctk.CTkToplevel(master)
            
        self.window.title("Driver Records")
        self.window.geometry("1000x800")
        self.window.resizable(True, True)
        
        self.create_widgets()
        self.load_drivers()
        
    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self.window,
            text="Driver Records",
            font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)
        
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        
        self.drivers_table = ttk.Treeview(
            self.window,
            columns=(
                "ID",
                "Driver Name",
                "Phone Number",
                "Address"
            ),
            show="headings",
            height=15
        )
        
        self.drivers_table.pack(
            padx=20,
            pady=20,
            fill="both",
            expand=True
        )
        
        self.drivers_table.bind(
            "<<TreeviewSelect>>",
            self.select_driver
        )
        self.drivers_table.heading("ID", text="ID")
        self.drivers_table.heading("Driver Name", text="Driver Name")
        self.drivers_table.heading("Phone Number", text="Phone Number")
        self.drivers_table.heading("Address", text="Address")
        
        self.drivers_table.column("ID", width=100)
        self.drivers_table.column("Driver Name", width=250)
        self.drivers_table.column("Phone Number", width=200)
        self.drivers_table.column("Address", width=350)
        
        self.update_button = ctk.CTkButton(
            self.window,
            text="Update Driver",
            command=self.open_update_window
        )
        self.update_button.pack(pady=10)
        
        self.delete_button = ctk.CTkButton(
            self.window,
            text="Delete Driver",
            command=self.delete_driver
        )
        self.delete_button.pack(pady=10)
        
    def select_driver(self, event):
        selected = self.drivers_table.focus()
        if not selected:
            return

        values = self.drivers_table.item(selected, "values")
        self.selected_driver_id = values[0]
        self.selected_driver = values
        print("Selected Driver ID:", self.selected_driver_id)

    def delete_driver(self):
        if not hasattr(self, "selected_driver_id"):
            messagebox.showerror("Error", "Please select a driver first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this driver?\n(Ensure they are not assigned to any bus first!)"
        )

        if not confirm:
            return

        connection = connect_database()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "DELETE FROM driver WHERE driver_id = ?",
                (self.selected_driver_id,)
            )
            connection.commit()
            messagebox.showinfo("Success", "Driver deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete driver: {e}")
        finally:
            connection.close()
            
        self.load_drivers()

    def open_update_window(self):
        if not hasattr(self, "selected_driver_id"):
            messagebox.showerror("Error", "Please select a driver first.")
            return

        self.update_window = ctk.CTkToplevel(self.window)
        self.update_window.title("Update Driver")
        self.update_window.geometry("500x500")
        self.update_window.resizable(False, False)

        title = ctk.CTkLabel(
            self.update_window,
            text="Update Driver",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Driver Name
        ctk.CTkLabel(self.update_window, text="Driver Name").pack()
        self.name_entry = ctk.CTkEntry(self.update_window, width=300)
        self.name_entry.pack(pady=5)
        self.name_entry.insert(0, self.selected_driver[1])

        # Phone Number
        ctk.CTkLabel(self.update_window, text="Phone Number").pack()
        self.phone_entry = ctk.CTkEntry(self.update_window, width=300)
        self.phone_entry.pack(pady=5)
        self.phone_entry.insert(0, self.selected_driver[2])

        # Address
        ctk.CTkLabel(self.update_window, text="Address").pack()
        self.address_entry = ctk.CTkEntry(self.update_window, width=300)
        self.address_entry.pack(pady=5)
        self.address_entry.insert(0, self.selected_driver[3])

        # Save Button
        self.save_button = ctk.CTkButton(
            self.update_window,
            text="Save Changes",
            command=self.update_driver
        )
        self.save_button.pack(pady=20)

    def update_driver(self):
        driver_name = self.name_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()

        if not all([driver_name, phone, address]):
            messagebox.showerror("Error", "All fields are required.")
            return

        connection = connect_database()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE driver
                SET driver_name = ?, driver_phone = ?, address = ?
                WHERE driver_id = ?
                """,
                (driver_name, phone, address, self.selected_driver_id)
            )
            connection.commit()
            messagebox.showinfo("Success", "Driver updated successfully!")
            self.update_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update driver: {e}")
        finally:
            connection.close()
            
        self.load_drivers()
        
    def load_drivers(self):
        for row in self.drivers_table.get_children():
            self.drivers_table.delete(row)
            
        connection = connect_database()
        cursor = connection.cursor()
        
        cursor.execute("SELECT driver_id, driver_name, driver_phone, address FROM driver")
        drivers = cursor.fetchall()
        
        for driver in drivers:
            self.drivers_table.insert(
                "",
                "end",
                values=driver
            )
        connection.close()
        
    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()

if __name__ == "__main__":
    app = DriverRecords()
    app.run()
