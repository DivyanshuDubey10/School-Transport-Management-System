import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class RouteManagement:
    
    def __init__(self, master=None):
        if master is None:
            self.window = ctk.CTk()
        else:
            self.window = ctk.CTkToplevel(master)
            
        self.window.title("Route Management")
        self.window.geometry("700x500")
        self.window.resizable(False, False)
        
        self.create_widgets()
    
    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self.window,
            text="Add New Route",
            font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)
        
        self.route_name_label = ctk.CTkLabel(
            self.window,
            text="Route Name",
            font=("Arial", 16)
        )
        self.route_name_label.pack(pady=(10, 5))
        
        self.route_name_entry = ctk.CTkEntry(
            self.window,
            width=300,
            placeholder_text="Enter Route Name"
        )
        self.route_name_entry.pack(pady=(0, 10))
        
        self.starting_point_label = ctk.CTkLabel(
            self.window,
            text="Starting Point",
            font=("Arial", 16)
        )
        self.starting_point_label.pack(pady=(10, 5))
        
        self.starting_point_entry = ctk.CTkEntry(
            self.window,
            width=300,
            placeholder_text="Enter Starting Point"
        )
        self.starting_point_entry.pack(pady=(0, 10))
        
        self.ending_point_label = ctk.CTkLabel(
            self.window,
            text="Ending Point",
            font=("Arial", 16)
        )
        self.ending_point_label.pack(pady=(10, 5))
        
        self.ending_point_entry = ctk.CTkEntry(
            self.window,
            width=300,
            placeholder_text="Enter Ending Point"
        )
        self.ending_point_entry.pack(pady=(0, 20))
        
        self.save_button = ctk.CTkButton(
            self.window,
            text="Save Route",
            command=self.save_route
        )
        self.save_button.pack(pady=10)
        
    def save_route(self):
        route_name = self.route_name_entry.get()
        starting_point = self.starting_point_entry.get()
        ending_point = self.ending_point_entry.get()
        
        if not route_name:
            messagebox.showerror("Error", "Route Name is required.")
            return
        
        if not starting_point:
            messagebox.showerror("Error", "Starting Point is required.")
            return
            
        if not ending_point:
            messagebox.showerror("Error", "Ending Point is required.")
            return

        connection = connect_database()
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                """ 
                INSERT INTO route (route_name, starting_point, ending_point)
                VALUES (?, ?, ?)
                """,
                (route_name, starting_point, ending_point)
            )
            connection.commit()
            messagebox.showinfo("Success", "Route saved successfully.")
            
            # Clear entries
            self.route_name_entry.delete(0, "end")
            self.starting_point_entry.delete(0, "end")
            self.ending_point_entry.delete(0, "end")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            connection.close()

    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()

if __name__ == "__main__":
    app = RouteManagement()
    app.run()
