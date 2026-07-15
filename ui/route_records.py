import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class RouteRecords:
    
    def __init__(self, master=None):
        if master is None:
            self.window = ctk.CTk()
        else:
            self.window = ctk.CTkToplevel(master)
            
        self.window.title("Route Records")
        self.window.geometry("1000x800")
        self.window.resizable(True, True)
        
        self.create_widgets()
        self.load_routes()
        
    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self.window,
            text="Route Records",
            font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)
        
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        
        self.routes_table = ttk.Treeview(
            self.window,
            columns=(
                "ID",
                "Route Name",
                "Starting Point",
                "Ending Point"
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
        self.routes_table.heading("Starting Point", text="Starting Point")
        self.routes_table.heading("Ending Point", text="Ending Point")
        
        self.routes_table.column("ID", width=100)
        self.routes_table.column("Route Name", width=250)
        self.routes_table.column("Starting Point", width=300)
        self.routes_table.column("Ending Point", width=300)
        
        self.update_button = ctk.CTkButton(
            self.window,
            text="Update Route",
            command=self.open_update_window
        )
        self.update_button.pack(pady=10)
        
        self.delete_button = ctk.CTkButton(
            self.window,
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

        connection = connect_database()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "DELETE FROM route WHERE route_id = ?",
                (self.selected_route_id,)
            )
            connection.commit()
            messagebox.showinfo("Success", "Route deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete route: {e}")
        finally:
            connection.close()
            
        self.load_routes()

    def open_update_window(self):
        if not hasattr(self, "selected_route_id"):
            messagebox.showerror("Error", "Please select a route first.")
            return

        self.update_window = ctk.CTkToplevel(self.window)
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

        # Starting Point
        ctk.CTkLabel(self.update_window, text="Starting Point").pack()
        self.start_entry = ctk.CTkEntry(self.update_window, width=300)
        self.start_entry.pack(pady=5)
        self.start_entry.insert(0, self.selected_route[2])

        # Ending Point
        ctk.CTkLabel(self.update_window, text="Ending Point").pack()
        self.end_entry = ctk.CTkEntry(self.update_window, width=300)
        self.end_entry.pack(pady=5)
        self.end_entry.insert(0, self.selected_route[3])

        # Save Button
        self.save_button = ctk.CTkButton(
            self.update_window,
            text="Save Changes",
            command=self.update_route
        )
        self.save_button.pack(pady=20)

    def update_route(self):
        route_name = self.name_entry.get()
        starting_point = self.start_entry.get()
        ending_point = self.end_entry.get()

        if not all([route_name, starting_point, ending_point]):
            messagebox.showerror("Error", "All fields are required.")
            return

        connection = connect_database()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE route
                SET route_name = ?, starting_point = ?, ending_point = ?
                WHERE route_id = ?
                """,
                (route_name, starting_point, ending_point, self.selected_route_id)
            )
            connection.commit()
            messagebox.showinfo("Success", "Route updated successfully!")
            self.update_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update route: {e}")
        finally:
            connection.close()
            
        self.load_routes()
        
    def load_routes(self):
        for row in self.routes_table.get_children():
            self.routes_table.delete(row)
            
        connection = connect_database()
        cursor = connection.cursor()
        
        cursor.execute("SELECT route_id, route_name, starting_point, ending_point FROM route")
        routes = cursor.fetchall()
        
        for route in routes:
            self.routes_table.insert(
                "",
                "end",
                values=route
            )
        connection.close()
        
    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()

if __name__ == "__main__":
    app = RouteRecords()
    app.run()
