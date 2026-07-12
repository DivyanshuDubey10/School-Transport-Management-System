from tkinter import ttk
import customtkinter as ctk
from tkinter import messagebox
from database import connect_database

class ParentRecords:
    
    def __init__(self):
        self.window = ctk.CTk()
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
        
        self.parents_table = ttk.Treeview(
            self.window,
            columns=(
                "ID",
                "Name",
                "Username",
                "Phone",
                "Email",
                "Address"
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
        self.parents_table.heading("Username", text="Username")
        self.parents_table.heading("Phone", text="Phone")
        self.parents_table.heading("Email", text="Email")
        self.parents_table.heading("Address", text="Address")
        
        self.parents_table.column("ID", width=60)
        self.parents_table.column("Name", width=180)
        self.parents_table.column("Username", width=150)
        self.parents_table.column("Phone", width=150)
        self.parents_table.column("Phone", width=140)
        self.parents_table.column("Email", width=200)
        self.parents_table.column("Address", width=220)
        
    def select_parent(self, event):
        print("Parent Selected")
        
    def load_parents(self):
        connection = connect_database()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM parent")
        
        parents = cursor.fetchall()
        
        for parents in parents:
            self.parents_table.insert(
                "",
                "end",
                values= parents
            )
        connection.close()
        
    def run(self):
        self.window.mainloop()
        

        