import customtkinter as ctk
from tkinter import ttk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class StudentRecords:
    
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Student Records")
        self.window.geometry("1200x700")
        self.window.resizable(True, True)
        
        self.create_widgets()
        self.load_students()
        
    def run(self):
        self.window.mainloop()
        
    def create_widgets(self):
        
        self.title = ctk.CTkLabel(
            self.window,
            text="Student Records",
            font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)
        
        self.students_table = ttk.Treeview(
            self.window,
            columns=(
                "ID",
                "Name",
                "Class",
                "Parent",
                "Phone",
                "Address",
                "Bus",
                "Route",
                "Fee"
            ),
            show="headings",
            height=18
        )
        self.students_table.heading("ID", text="ID")
        self.students_table.heading("Name", text="Student Name")
        self.students_table.heading("Class", text="Class")
        self.students_table.heading("Parent", text="Parent ID")
        self.students_table.heading("Phone", text="Phone")
        self.students_table.heading("Address", text="Address")
        self.students_table.heading("Bus", text="Bus ID")
        self.students_table.heading("Route", text="Route ID")
        self.students_table.heading("Fee", text="Fee Status")
        
        self.students_table.column("ID", width=60)
        self.students_table.column("Name", width=180)
        self.students_table.column("Class", width=80)
        self.students_table.column("Parent", width=80)
        self.students_table.column("Phone", width=120)
        self.students_table.column("Address", width=200)
        self.students_table.column("Bus", width=80)
        self.students_table.column("Route", width=80)
        self.students_table.column("Fee", width=120)
        
        self.students_table.pack(padx=20, pady=20, fill="both", expand=True)
        
    def load_students(self):

        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM student")

        students = cursor.fetchall()

        for student in students:
            self.students_table.insert(
                "",
                "end",
                values=student
            )

        connection.close()
        
        if __name__ == "__main__":
            app = StudentRecords()
            app.run()