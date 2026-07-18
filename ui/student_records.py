import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class StudentRecords(ctk.CTkFrame):
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.create_widgets()
        self.load_students()
        

        
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
            self,
            text="Student Records",
            font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)
        
        # Search Frame
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search by Name or Class...", width=300)
        self.search_entry.pack(side="left", padx=10)
        
        self.search_button = ctk.CTkButton(self.search_frame, text="Search", width=100, command=self.load_students)
        self.search_button.pack(side="left")
        
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        
        self.students_table = ttk.Treeview(
            self,
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
        
        self.students_table.column("ID", width=80)
        self.students_table.column("Name", width=220)
        self.students_table.column("Class", width=100)
        self.students_table.column("Parent", width=100)
        self.students_table.column("Phone", width=150)
        self.students_table.column("Address", width=300)
        self.students_table.column("Bus", width=100)
        self.students_table.column("Route", width=100)
        self.students_table.column("Fee", width=150)
        
        self.students_table.pack(padx=20, pady=20, fill="both", expand=True)
        self.update_button = ctk.CTkButton(
            self,
            text="Update Student",
            command=self.open_update_window
        )
        self.update_button.pack(pady=10)
        
        self.delete_button = ctk.CTkButton(
            self,
            text="Delete Student",
            command = self.delete_student
        )
        self.delete_button.pack(pady=10)
        
    def delete_student(self):
        
        if not hasattr(self, "selected_student_id"):
                messagebox.showerror(
                    "Error",
                    "Please select a student first."
                )
                return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this student?"
        )

        if not confirm:
            return
        
        from dal import db_dal

        try:
            success = db_dal.delete_student(self.selected_student_id)
            if success:
                messagebox.showinfo("Success", "Student deleted successfully!")
            else:
                messagebox.showerror("Error", "Could not delete student.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete student: {e}")

        self.load_students()
                
    def open_update_window(self):

        if not hasattr(self, "selected_student_id"):
            messagebox.showerror(
                "Error",
                "Please select a student first."
            )
            return

        self.update_window = ctk.CTkToplevel(self)
        self.update_window.title("Update Student")
        self.update_window.geometry("500x500")
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
        
        student_name = self.name_entry.get()
        student_class = self.class_entry.get()
        parent_id = self.parent_entry.get()
        route_id = self.route_entry.get()
        fee_status = self.fee_entry.get()
        
        from dal import db_dal

        try:
            success = db_dal.update_student(
                self.selected_student_id,
                student_name,
                student_class,
                parent_id,
                route_id,
                fee_status
            )
            
            if success:
                messagebox.showinfo("Success", "Student updated successfully!")
                self.update_window.destroy()
            else:
                messagebox.showerror("Error", "Could not update student.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {e}")

        self.load_students()
        

    def load_students(self):
        
        for row in self.students_table.get_children():
            self.students_table.delete(row)

        search_query = ""
        if hasattr(self, 'search_entry'):
            search_query = self.search_entry.get().strip()

        from dal import db_dal
        students = db_dal.get_all_students(search_query=search_query)

        for student in students:
            self.students_table.insert(
                "",
                "end",
                values=student
            )