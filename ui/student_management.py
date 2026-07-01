import customtkinter as ctk
from tkinter import messagebox
from database import connect_database

class StudentManagement:
    def __init__(self):

        self.window = ctk.CTk()
        self.window.title("Student Management")
        self.window.geometry("800x700")
        self.window.resizable(False, False)
 
        self.create_widgets()

    def create_widgets(self):

        # Title
        self.title = ctk.CTkLabel(
            self.window, text="Student Management", font=("Arial", 28, "bold")
        )
        self.title.pack(pady=20)

        # Student Name
        self.student_name_label = ctk.CTkLabel(self.window, text="Student Name", placeholder_text="Enter Student Name")
        self.student_name_label.pack()

        self.student_name_entry = ctk.CTkEntry(self.window, width=300)
        self.student_name_entry.pack(pady=10)

        # Student Class
        self.student_class_label = ctk.CTkLabel(self.window, text="Student Class", placeholder_text="Enter Student Class")
        self.student_class_label.pack()

        self.student_class_entry = ctk.CTkEntry(self.window, width=300)
        self.student_class_entry.pack(pady=10)

        # Parent ID
        self.parent_id_label = ctk.CTkLabel(self.window, text="Parent ID", placeholder_text="Enter Parent ID")
        self.parent_id_label.pack()

        self.parent_id_entry = ctk.CTkEntry(self.window, width=300)
        self.parent_id_entry.pack(pady=10)

        # Phone
        self.phone_label = ctk.CTkLabel(self.window, text="Phone", placeholder_text="Enter Phone Number")
        self.phone_label.pack()

        self.phone_entry = ctk.CTkEntry(self.window, width=300)
        self.phone_entry.pack(pady=10)

        # Address
        self.address_label = ctk.CTkLabel(self.window, text="Address", placeholder_text="Enter Address")
        self.address_label.pack()

        self.address_entry = ctk.CTkEntry(self.window, width=300)
        self.address_entry.pack(pady=10)

        # Bus ID
        self.bus_id_label = ctk.CTkLabel(self.window, text="Bus ID", placeholder_text="Enter Bus ID")
        self.bus_id_label.pack()

        self.bus_id_entry = ctk.CTkEntry(self.window, width=300)
        self.busid_entry.pack(pady=10)

        # Route
        self.route_id_label = ctk.CTkLabel(self.window, text="Route ID", placeholder_text="Enter Route ID")
        self.route_id_label.pack()

        self.routeid_entry = ctk.CTkEntry(self.window, width=300)
        self.routeid_entry.pack(pady=10)

        # Save Button
        self.save_button = ctk.CTkButton(
            self.window, text="Save Student", command=self.save_student
        )
        self.save_button.pack(pady=25)

    def save_student(self):
        
        student_name= self.student_name_entry.get()
        student_class = self.student_class_entry.get()
        parent_id = self.parent_id_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()
        bus_id = self.busid_entry.get()
        route_id = self.routeid_entry.get()
        
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute("""
                       INSERT INTO student
                       (student_name, student_class, parent_id, phone, address, bus_id, route_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_name,
            student_class,
            parent_id,
            phone,
            address,
            bus_id,
            route_id
        ))
        
        if not student_name:
            messagebox.showerror("Error", "Student Name is required.")
            return

        if not student_class:
            messagebox.showerror("Error", "Student Class is required.")
            return

        if not parent_id:
            messagebox.showerror("Error", "Parent ID is required.")
            return

        if not phone:
            messagebox.showerror("Error", "Phone Number is required.")
            return

        if not address:
            messagebox.showerror("Error", "Address is required.")
            return

        if not bus_id:
            messagebox.showerror("Error", "Bus ID is required.")
            return

        if not route_id:
            messagebox.showerror("Error", "Route ID is required.")
            return
        
        self.student_name_entry.delete(0, "end")
        self.student_class_entry.delete(0, "end")
        self.parent_id_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
        self.bus_id_entry.delete(0, "end")
        self.route_id_entry.delete(0, "end")

        connection.commit()
        connection.close()
        messagebox.showinfo(
            "Success",
            "Student added successfully!"
        )

    def run(self):
        self.window.mainloop()
