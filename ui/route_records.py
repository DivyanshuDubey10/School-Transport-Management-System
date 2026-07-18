import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class RouteRecords(ctk.CTkFrame):
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.create_widgets()
        self.load_routes()
        
    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self,
            text="Route Records",
            font=("Arial", 28, "bold") 
        )
        self.title.pack(pady=20)
        
        # Search Frame
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search by Route Name...", width=300)
        self.search_entry.pack(side="left", padx=10)
        
        self.search_button = ctk.CTkButton(self.search_frame, text="Search", width=100, command=self.load_routes)
        self.search_button.pack(side="left")
        
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        
        self.routes_table = ttk.Treeview(
            self,
            columns=(
                "ID",
                "Route Name"
            ),
            show="headings",
            height=15
        )
        
        self.routes_table.pack(
            padx=20,
            pady=20,
            fill="both",
            expand=True
        )
        
        self.routes_table.bind(
            "<<TreeviewSelect>>",
            self.select_route
        )
        self.routes_table.heading("ID", text="ID")
        self.routes_table.heading("Route Name", text="Route Name")
        
        self.routes_table.column("ID", width=100)
        self.routes_table.column("Route Name", width=500)
        
        self.update_button = ctk.CTkButton(
            self,
            text="Update Route",
            command=self.open_update_window
        )
        self.update_button.pack(pady=10)
        
        self.delete_button = ctk.CTkButton(
            self,
            text="Delete Route",
            command=self.delete_route
        )
        self.delete_button.pack(pady=10)
        
    def select_route(self, event):
        selected = self.routes_table.focus()
        if not selected:
            return

        values = self.routes_table.item(selected, "values")
        self.selected_route_id = values[0]
        self.selected_route = values
        print("Selected Route ID:", self.selected_route_id)

    def delete_route(self):
        if not hasattr(self, "selected_route_id"):
            messagebox.showerror("Error", "Please select a route first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this route?\n(Ensure no buses or students are assigned to this route first!)"
        )

        if not confirm:
            return

        from dal import db_dal
        
        try:
            success = db_dal.delete_route(self.selected_route_id)
            if success:
                messagebox.showinfo("Success", "Route deleted successfully!")
            else:
                messagebox.showerror("Error", "Could not delete route.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete route: {e}")
            
        self.load_routes()

    def open_update_window(self):
        if not hasattr(self, "selected_route_id"):
            messagebox.showerror("Error", "Please select a route first.")
            return

        self.update_window = ctk.CTkToplevel(self)
        self.update_window.title("Update Route")
        self.update_window.geometry("500x500")
        self.update_window.resizable(False, False)

        title = ctk.CTkLabel(
            self.update_window,
            text="Update Route",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Route Name
        ctk.CTkLabel(self.update_window, text="Route Name").pack()
        self.name_entry = ctk.CTkEntry(self.update_window, width=300)
        self.name_entry.pack(pady=5)
        self.name_entry.insert(0, self.selected_route[1])


        # Save Button
        self.save_button = ctk.CTkButton(
            self.update_window,
            text="Save Changes",
            command=self.update_route
        )
        self.save_button.pack(pady=20)

    def update_route(self):
        route_name = self.name_entry.get()

        if not route_name:
            messagebox.showerror("Error", "All fields are required.")
            return

        from dal import db_dal

        try:
            success = db_dal.update_route(self.selected_route_id, route_name)
            if success:
                messagebox.showinfo("Success", "Route updated successfully!")
                self.update_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to update route.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update route: {e}")
            
        self.load_routes()
        
    def load_routes(self):
        for row in self.routes_table.get_children():
            self.routes_table.delete(row)
            
        search_query = ""
        if hasattr(self, 'search_entry'):
            search_query = self.search_entry.get().strip()
            
        from dal import db_dal
        routes = db_dal.get_all_routes(search_query=search_query)
        
        for route in routes:
            self.routes_table.insert(
                "",
                "end",
                values=route
            )
        
