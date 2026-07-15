import customtkinter as ctk
from ui.student_management import StudentManagement
from ui.student_records import StudentRecords
from ui.parent_management import ParentManagement
from ui.parent_records import ParentRecords
from ui.route_management import RouteManagement
from ui.bus_management import BusManagement
from ui.route_records import RouteRecords
from ui.driver_management import DriverManagement
from ui.driver_records import DriverRecords

class AdminDashboard:
    
    def __init__(self, master=None):
        self.master = master
        if master is None:
            self.window = ctk.CTk()
        else:
            self.window = ctk.CTkToplevel(master)
            # If we close the admin dashboard, we should quit the app
            self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.window.title("Admin Dashboard")
        self.window.geometry("900x600")
        self.window.resizable(False, False)
        
        self.create_widgets()
        
    def on_close(self):
        if self.master:
            self.master.destroy()
        else:
            self.window.destroy()
            
    def create_widgets(self):
        
        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(
            self.window, 
            width=200, 
            corner_radius=0
        )
        self.sidebar_frame.pack(
            side="left", 
            fill="y"
        )
        
        # Sidebar Title
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_frame,
            text="STMS",
            font=("Arial", 24, "bold")
        )
        self.sidebar_title.pack(pady=20)
        
        # Main Frame
        self.main_frame= ctk.CTkFrame(
            self.window,
            corner_radius=0
        )
        self.main_frame.pack(
            side="right",
            fill="both",
            expand=True
        )
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="School Transport Management System",
            font=("Arial", 30, "bold")
        )
        self.title_label.pack(pady=20)
        
        # Welcome Label
        self.welcome_label = ctk.CTkLabel(
            self.main_frame,
            text="Welcome, Admin!",
            font=("Arial", 20)
        )
        self.welcome_label.pack(pady=10)
        
        # Dashboard Button
        self.dashboard_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Dashboard",
            width=170
        )
        self.dashboard_button.pack(pady=10)

        # Student Management Button
        self.student_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Student Management",
            width=170,
            command=self.open_student_management
        )
        self.student_button.pack(pady=10)
        
        # Student Records Button
        self.student_records_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Student Records",
            width=170,
            command=self.open_student_records
        )
        self.student_records_button.pack(pady=10, padx=20)

        # Parent Management Button
        self.parent_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Parent Management",
            width=170,
            command=self.open_parent_management
        )
        self.parent_button.pack(pady=10)
        
        # Student Record Button
        self.parent_record_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Parent Records",
            width=170,
            command=self.open_parent_records
        )
        self.parent_record_button.pack(pady="10")

        # Bus Management Button
        self.bus_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Bus Management",
            width=170,
            command=self.open_bus_management
        )
        self.bus_button.pack(pady=10)

        # Route Management Button
        self.route_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Route Management",
            width=170,
            command=self.open_route_management
        )
        self.route_button.pack(pady=10)
        
        # Route Records Button
        self.route_records_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Route Records",
            width=170,
            command=self.open_route_records
        )
        self.route_records_button.pack(pady=10)

        # Driver Management Button
        self.driver_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Driver Management",
            width=170,
            command=self.open_driver_management
        )
        self.driver_button.pack(pady=10)

        # Driver Records Button
        self.driver_records_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Driver Records",
            width=170,
            command=self.open_driver_records
        )
        self.driver_records_button.pack(pady=10)

        # Logout Button
        self.logout_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Logout",
            width=170,
        )
        self.logout_button.pack(pady=10)
        
    def open_student_management(self):
        student=StudentManagement(master=self.window)
        student.run()
        
    def open_student_records(self):
        records=StudentRecords(master=self.window)
        records.run()
        
    def open_parent_management(self):
        parent=ParentManagement(master=self.window)
        parent.run()
        
    def open_parent_records(self):
        records=ParentRecords(master=self.window)
        records.run()
        
    def open_bus_management(self):
        bus_mgmt = BusManagement(master=self.window)
        bus_mgmt.run()
        
    def open_route_management(self):
        route_mgmt = RouteManagement(master=self.window)
        route_mgmt.run()
        
    def open_route_records(self):
        route_recs = RouteRecords(master=self.window)
        route_recs.run()
        
    def open_driver_management(self):
        driver_mgmt = DriverManagement(master=self.window)
        driver_mgmt.run()
        
    def open_driver_records(self):
        driver_recs = DriverRecords(master=self.window)
        driver_recs.run()
        
    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()
        