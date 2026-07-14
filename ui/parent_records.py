from tkinter import ttk
import customtkinter as ctk
from tkinter import messagebox
from database import connect_database

class ParentRecords:
    
    def __init__(self, master=None):
        if master is None:
            self.window = ctk.CTk()
        else:
            self.window = ctk.CTkToplevel(master)
            
        self.window.title("Parent Records")
        self.window.geometry("1200x1000")
        self.window.resizable(True, True)
        
        self.create_widgets()
        self.load_parents()
        
    def create_widgets(self):
        self.title = ctk.CTkLabel(
            self.window,
            text="Parents Records",
            font=("Arial", 28,"bold")
        )
        self.title.pack(pady="20") 
        
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        
        self.parents_table = ttk.Treeview(
            self.window,
            columns=(
                "ID",
                "Name",
                "Phone",
                "Address",
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
        self.parents_table.heading("Username", text="Username")
        
        self.parents_table.column("ID", width=100)
        self.parents_table.column("Name", width=250)
        self.parents_table.column("Phone", width=200)
        self.parents_table.column("Address", width=350)
        self.parents_table.column("Username", width=200)
        
        self.update_button = ctk.CTkButton(
            self.window,
            text="Update Parent",
            command=self.open_update_window
        )
        self.update_button.pack(pady=10)
        
        self.delete_button = ctk.CTkButton(
            self.window,
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

        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM parent WHERE parent_id = ?",
            (self.selected_parent_id,)
        )

        connection.commit()
        connection.close()

        messagebox.showinfo("Success", "Parent deleted successfully!")
        self.load_parents()

    def open_update_window(self):
        if not hasattr(self, "selected_parent_id"):
            messagebox.showerror("Error", "Please select a parent first.")
            return

        self.update_window = ctk.CTkToplevel(self.window)
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

        # Username
        ctk.CTkLabel(self.update_window, text="Username").pack()
        self.username_entry = ctk.CTkEntry(self.update_window, width=300)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, self.selected_parent[4])

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
        username = self.username_entry.get()

        if not all([parent_name, phone, address, username]):
            messagebox.showerror("Error", "All fields are required.")
            return

        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE parent
            SET parent_name = ?, phone = ?, address = ?, username = ?
            WHERE parent_id = ?
            """,
            (parent_name, phone, address, username, self.selected_parent_id)
        )

        connection.commit()
        connection.close()

        messagebox.showinfo("Success", "Parent updated successfully!")
        self.update_window.destroy()
        self.load_parents()
        
    def load_parents(self):
        for row in self.parents_table.get_children():
            self.parents_table.delete(row)
            
        connection = connect_database()
        cursor = connection.cursor()
        
        cursor.execute("SELECT parent_id, parent_name, phone, address, username FROM parent")
        
        parents = cursor.fetchall()
        
        for parent in parents:
            self.parents_table.insert(
                "",
                "end",
                values=parent
            )
        connection.close()
        
    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()
        

        