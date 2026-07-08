import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class StudentRecords:
    
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Student Records")
        self.window.geometry("1200x900")
        self.window.resizable(True, True)
        
        self.create_widgets()
        self.load_students()
        
    def run(self):
        self.window.mainloop()
        
    def select_student(self, event):
        selected = self.students_table.focus()
        if not selected:
            return

        values = self.students_table.item(selected, "values")

        self.selected_student_id = values[0]
        self.selected_student = values

        print("Selected Student ID:", self.selected_student_id)   
                 
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
        
        self.students_table.bind(
            "<<TreeviewSelect>>",
            self.select_student
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
        self.update_button = ctk.CTkButton(
            self.window,
            text="Update Student",
            command=self.open_update_window
        )
        self.update_button.pack(pady=10)
        
    def open_update_window(self):

        if not hasattr(self, "selected_student_id"):
            messagebox.showerror(
                "Error",
                "Please select a student first."
            )
            return

        self.update_window = ctk.CTkToplevel(self.window)
        self.update_window.title("Update Student")
        self.update_window.geometry("500x700")
        self.update_window.resizable(False, False)

        title = ctk.CTkLabel(
            self.update_window,
            text="Update Student",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Student Name
        ctk.CTkLabel(self.update_window, text="Student Name").pack()
        self.name_entry = ctk.CTkEntry(self.update_window, width=300)
        self.name_entry.pack(pady=5)
        self.name_entry.insert(0, self.selected_student[1])

        # Student Class
        ctk.CTkLabel(self.update_window, text="Student Class").pack()
        self.class_entry = ctk.CTkEntry(self.update_window, width=300)
        self.class_entry.pack(pady=5)
        self.class_entry.insert(0, self.selected_student[2])

        # Parent ID
        ctk.CTkLabel(self.update_window, text="Parent ID").pack()
        self.parent_entry = ctk.CTkEntry(self.update_window, width=300)
        self.parent_entry.pack(pady=5)
        self.parent_entry.insert(0, self.selected_student[3])

        # Phone
        ctk.CTkLabel(self.update_window, text="Phone").pack()
        self.phone_entry = ctk.CTkEntry(self.update_window, width=300)
        self.phone_entry.pack(pady=5)
        self.phone_entry.insert(0, self.selected_student[4])

        # Address
        ctk.CTkLabel(self.update_window, text="Address").pack()
        self.address_entry = ctk.CTkEntry(self.update_window, width=300)
        self.address_entry.pack(pady=5)
        self.address_entry.insert(0, self.selected_student[5])

        # Bus ID
        ctk.CTkLabel(self.update_window, text="Bus ID").pack()
        self.bus_entry = ctk.CTkEntry(self.update_window, width=300)
        self.bus_entry.pack(pady=5)
        self.bus_entry.insert(0, self.selected_student[6])

        # Route ID
        ctk.CTkLabel(self.update_window, text="Route ID").pack()
        self.route_entry = ctk.CTkEntry(self.update_window, width=300)
        self.route_entry.pack(pady=5)
        self.route_entry.insert(0, self.selected_student[7])

        # Fee Status
        ctk.CTkLabel(self.update_window, text="Fee Status").pack()
        self.fee_entry = ctk.CTkEntry(self.update_window, width=300)
        self.fee_entry.pack(pady=5)
        self.fee_entry.insert(0, self.selected_student[8])

        # Save Button
        self.save_button = ctk.CTkButton(
            self.update_window,
            text="Save Changes",
            command = self.update_student
        )
        self.save_button.pack(pady=20)
        
    def update_student(self):
        
        print("Update function called")
        
        student_name = self.name_entry.get()
        student_class = self.class_entry.get()
        parent_id = self.parent_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()
        bus_id = self.bus_entry.get()
        route_id = self.route_entry.get()
        fee_status = self.fee_entry.get()
        
        connection = connect_database()
        cursor = connection.cursor()
        
        cursor.execute(
            """
                UPDATE student
                SET
                    student_name = ?,
                    student_class = ?,
                    parent_id = ?,
                    phone = ?,
                    address = ?,
                    bus_id = ?,
                    route_id = ?,
                    fee_status = ?
                WHERE student_id = ?
                """,
            (
                student_name,
                student_class,
                parent_id,
                phone,
                address,
                bus_id,
                route_id,
                fee_status,
                self.selected_student_id
            )
        )

        connection.commit()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Student updated successfully!"
        )

        self.update_window.destroy()

        self.load_students()
        

    def load_students(self):
        
        for row in self.students_table.get_children():
            self.students_table.delete(row)

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