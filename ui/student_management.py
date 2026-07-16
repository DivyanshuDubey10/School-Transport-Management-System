import customtkinter as ctk
from tkinter import messagebox
from database import connect_database
from tkinter import ttk


class StudentManagement:
    def __init__(self, master=None):
        if master is None:
            self.window = ctk.CTk()
        else:
            self.window = ctk.CTkToplevel(master)
            
        self.window.title("Student Management")
        self.window.geometry("800x800")
        self.window.resizable(False, False)
        
        self.fetch_dropdown_data()
        self.create_widgets()
        
    def fetch_dropdown_data(self):
        connection = connect_database()
        cursor = connection.cursor()
        
        # Fetch parents
        cursor.execute("SELECT parent_id, parent_name FROM parent")
        self.parent_options = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
        if not self.parent_options: self.parent_options = [""]
        
        # Fetch routes and their assigned buses
        cursor.execute("SELECT r.route_id, r.route_name, b.bus_number FROM route r LEFT JOIN bus b ON r.route_id = b.route_id")
        self.route_options = []
        for row in cursor.fetchall():
            bus_str = f" (Bus: {row[2]})" if row[2] else " (No Bus)"
            self.route_options.append(f"{row[0]} - {row[1]}{bus_str}")
        if not self.route_options: self.route_options = [""]
        
        connection.close()

    def create_widgets(self):

        # Title
        self.title = ctk.CTkLabel(
            self.window, text="Student Management", font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)

        # Student Name
        self.student_name_label = ctk.CTkLabel(self.window, text="Student Name")
        self.student_name_label.pack()

        self.student_name_entry = ctk.CTkEntry(
            self.window, width=300, placeholder_text="Enter Student Name"
        )
        self.student_name_entry.pack(pady=10)

        # Student Class
        self.student_class_label = ctk.CTkLabel(self.window, text="Student Class")
        self.student_class_label.pack()

        self.student_class_entry = ctk.CTkEntry(
            self.window, width=300, placeholder_text="Enter Student Class"
        )
        self.student_class_entry.pack(pady=10)

        self.parent_id_label = ctk.CTkLabel(self.window, text="Parent")
        self.parent_id_label.pack()

        self.parent_id_entry = ctk.CTkComboBox(
            self.window, width=300, values=self.parent_options
        )
        self.parent_id_entry.pack(pady=10)
        self.parent_id_entry.set("Select Parent" if not self.parent_options[0] == "" else "No Parents Available")



        self.route_id_label = ctk.CTkLabel(self.window, text="Route")
        self.route_id_label.pack()

        self.route_id_entry = ctk.CTkComboBox(
            self.window, width=300, values=self.route_options
        )
        self.route_id_entry.pack(pady=10)
        self.route_id_entry.set("Select Route" if not self.route_options[0] == "" else "No Routes Available")

        # Save Button
        self.save_button = ctk.CTkButton(
            self.window, text="Save Student", command=self.save_student
        )
        self.save_button.pack(pady=25)

        # Student List Title
        self.list_label = ctk.CTkLabel(
            self.window, text="Student Records", font=("Arial", 20, "bold")
        )
        self.list_label.pack(pady=10)

        # Student Table
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
                "Fee",
            ),
            show="headings",
            height=8,
        )

        # Headings
        # Headings
        self.students_table.heading("ID", text="ID")
        self.students_table.heading("Name", text="Student Name")
        self.students_table.heading("Class", text="Class")
        self.students_table.heading("Parent", text="Parent ID")
        self.students_table.heading("Phone", text="Phone")
        self.students_table.heading("Address", text="Address")
        self.students_table.heading("Bus", text="Bus ID")
        self.students_table.heading("Route", text="Route ID")
        self.students_table.heading("Fee", text="Fee Status")

        # Column Widths
        self.students_table.column("ID", width=50, anchor="center")
        self.students_table.column("Name", width=150)
        self.students_table.column("Class", width=80, anchor="center")
        self.students_table.column("Parent", width=80, anchor="center")
        self.students_table.column("Phone", width=120)
        self.students_table.column("Address", width=150)
        self.students_table.column("Bus", width=70, anchor="center")
        self.students_table.column("Route", width=70, anchor="center")
        self.students_table.column("Fee", width=100, anchor="center")

        self.students_table.pack(padx=10, pady=10, fill="both", expand=True)
        self.load_students()

    def load_students(self):
        for row in self.students_table.get_children():
            self.students_table.delete(row)

        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute("SELECT s.student_id, s.student_name, s.student_class, s.parent_id, p.phone, p.address, b.bus_id, s.route_id, s.fee_status FROM student s JOIN parent p ON s.parent_id = p.parent_id LEFT JOIN bus b ON s.route_id = b.route_id")
        students = cursor.fetchall()
        print(students)

        for student in students:
            self.students_table.insert("", "end", values=student)

        connection.close()

    def save_student(self):

        student_name = self.student_name_entry.get()
        student_class = self.student_class_entry.get()
        parent_selection = self.parent_id_entry.get()

        route_selection = self.route_id_entry.get()
        fee_status = "Pending"
        
        # Extract IDs from the dropdown string, default to empty if not selected properly
        parent_id = parent_selection.split(" - ")[0] if " - " in parent_selection else ""
        route_id = route_selection.split(" - ")[0] if " - " in route_selection else ""

        # Validation
        if not student_name:
            messagebox.showerror("Error", "Student Name is required.")
            return

        if not student_class:
            messagebox.showerror("Error", "Student Class is required.")
            return

        if not parent_id:
            messagebox.showerror("Error", "Parent ID is required.")
            return

        if not route_id:
            messagebox.showerror("Error", "Route ID is required.")
            return

        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            """
                INSERT INTO student
                (
                    student_name,
                    student_class,
                    parent_id,
                    route_id,
                    fee_status
                )
                VALUES (?, ?, ?, ?, ?)
                """,
            (
                student_name,
                student_class,
                parent_id,
                route_id,
                fee_status,
            ),
        )

        connection.commit()
        self.load_students()

        messagebox.showinfo("Success", "Student added successfully!")
        connection.close()

        self.student_name_entry.delete(0, "end")
        self.student_class_entry.delete(0, "end")
        self.parent_id_entry.set("Select Parent")
        self.route_id_entry.set("Select Route")

    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()
