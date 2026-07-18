from tkinter import ttk
import customtkinter as ctk
from tkinter import messagebox
from database import connect_database

class ParentRecords(ctk.CTkFrame):
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.create_widgets()
        self.load_parents()
        
    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self,
            text="Parents Records",
            font=("Arial", 28,"bold")
        )
        self.title.pack(pady="20") 
        
        # Search Frame
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search by Name, Username or Phone...", width=300)
        self.search_entry.pack(side="left", padx=10)
        
        self.search_button = ctk.CTkButton(self.search_frame, text="Search", width=100, command=self.load_parents)
        self.search_button.pack(side="left")
        
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        
        self.parents_table = ttk.Treeview(
            self,
            columns=(
                "ID",
                "Name",
                "Phone",
                "Address",
                "Pickup Point",
                "Username"
            ),
            show="headings",
            height=18
        )
        
        self.parents_table.pack(
            padx=20,
            pady=20,
            fill="both",
            expand=True
        )
        
        self.parents_table.bind(
            "<<TreeviewSelect>>",
            self.select_parent
        )
        self.parents_table.heading("ID", text="ID")
        self.parents_table.heading("Name", text="Parent Name")
        self.parents_table.heading("Phone", text="Phone")
        self.parents_table.heading("Address", text="Address")
        self.parents_table.heading("Pickup Point", text="Pickup Point")
        self.parents_table.heading("Username", text="Username")
        
        self.parents_table.column("ID", width=100)
        self.parents_table.column("Name", width=200)
        self.parents_table.column("Phone", width=150)
        self.parents_table.column("Address", width=250)
        self.parents_table.column("Pickup Point", width=200)
        self.parents_table.column("Username", width=150)
        
        self.update_button = ctk.CTkButton(
            self,
            text="Update Parent",
            command=self.open_update_window
        )
        self.update_button.pack(pady=10)
        
        self.delete_button = ctk.CTkButton(
            self,
            text="Delete Parent",
            command=self.delete_parent
        )
        self.delete_button.pack(pady=10)
        
    def select_parent(self, event):
        selected = self.parents_table.focus()
        if not selected:
            return

        values = self.parents_table.item(selected, "values")
        self.selected_parent_id = values[0]
        self.selected_parent = values
        print("Selected Parent ID:", self.selected_parent_id)

    def delete_parent(self):
        if not hasattr(self, "selected_parent_id"):
            messagebox.showerror("Error", "Please select a parent first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this parent?"
        )

        if not confirm:
            return

        from dal import db_dal
        
        success = db_dal.delete_parent(self.selected_parent_id)
        if not success:
            messagebox.showerror("Error", "Could not delete parent.")
            return

        messagebox.showinfo("Success", "Parent deleted successfully!")
        self.load_parents()

    def open_update_window(self):
        if not hasattr(self, "selected_parent_id"):
            messagebox.showerror("Error", "Please select a parent first.")
            return

        self.update_window = ctk.CTkToplevel(self)
        self.update_window.title("Update Parent")
        self.update_window.geometry("500x600")
        self.update_window.resizable(False, False)

        title = ctk.CTkLabel(
            self.update_window,
            text="Update Parent",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Name
        ctk.CTkLabel(self.update_window, text="Parent Name").pack()
        self.name_entry = ctk.CTkEntry(self.update_window, width=300)
        self.name_entry.pack(pady=5)
        self.name_entry.insert(0, self.selected_parent[1])

        # Phone
        ctk.CTkLabel(self.update_window, text="Phone").pack()
        self.phone_entry = ctk.CTkEntry(self.update_window, width=300)
        self.phone_entry.pack(pady=5)
        self.phone_entry.insert(0, self.selected_parent[2])

        # Address
        ctk.CTkLabel(self.update_window, text="Address").pack()
        self.address_entry = ctk.CTkEntry(self.update_window, width=300)
        self.address_entry.pack(pady=5)
        self.address_entry.insert(0, self.selected_parent[3])
        
        # Pickup Point
        ctk.CTkLabel(self.update_window, text="Pickup Point").pack()
        self.pickup_entry = ctk.CTkEntry(self.update_window, width=300)
        self.pickup_entry.pack(pady=5)
        self.pickup_entry.insert(0, self.selected_parent[4])

        # Username
        ctk.CTkLabel(self.update_window, text="Username").pack()
        self.username_entry = ctk.CTkEntry(self.update_window, width=300)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, self.selected_parent[5])

        # Save Button
        self.save_button = ctk.CTkButton(
            self.update_window,
            text="Save Changes",
            command=self.update_parent
        )
        self.save_button.pack(pady=20)

    def update_parent(self):
        parent_name = self.name_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()
        pickup_point = self.pickup_entry.get()
        username = self.username_entry.get()

        if not all([parent_name, phone, address, pickup_point, username]):
            messagebox.showerror("Error", "All fields are required.")
            return

        from dal import db_dal
        
        success = db_dal.update_parent(self.selected_parent_id, parent_name, phone, address, pickup_point, username)
        if not success:
            messagebox.showerror("Error", "Could not update parent.")
            return

        messagebox.showinfo("Success", "Parent updated successfully!")
        self.update_window.destroy()
        self.load_parents()
        
    def load_parents(self):
        for row in self.parents_table.get_children():
            self.parents_table.delete(row)
            
        search_query = ""
        if hasattr(self, 'search_entry'):
            search_query = self.search_entry.get().strip()
            
        from dal import db_dal
        parents = db_dal.get_all_parents(search_query=search_query)
        
        for parent in parents:
            self.parents_table.insert(
                "",
                "end",
                values=parent
            )
        