import customtkinter as ctk
from ui.student_management import StudentManagement

class AdminDashboard:
    
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Admin Dashboard")
        self.window.geometry("900x600")
        self.window.resizable(False, False)
        
        self.create_widgets()
            
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

        # Parent Management Button
        self.parent_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Parent Management",
            width=170
       )
        self.parent_button.pack(pady=10)

        # Bus Management Button
        self.bus_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Bus Management",
            width=170
        )
        self.bus_button.pack(pady=10)

        # Route Management Button
        self.route_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Route Management",
            width=170
        )
        self.route_button.pack(pady=10)

        # Logout Button
        self.logout_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Logout",
            width=170
        )
        self.logout_button.pack(pady=10)
        
    def open_student_management(self):
        student=StudentManagement()
        student.run()
        
    def run(self):
        self.window.mainloop()
        