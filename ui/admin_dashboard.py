import customtkinter as ctk
from ui.student_management import StudentManagement
from ui.student_records import StudentRecords
from ui.parent_management import ParentManagement
from ui.parent_records import ParentRecords
from ui.route_management import RouteManagement
from ui.bus_management import BusManagement
from ui.route_records import RouteRecords
import database

class DashboardHome(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller
        self.create_widgets()
        self.load_dashboard_stats()
        
    def load_dashboard_stats(self):
        try:
            from dal import db_dal
            stats = db_dal.get_dashboard_stats()
            
            self.card1_value.configure(text=str(stats["total_students"]))
            self.card2_value.configure(text=str(stats["total_buses"]))
            self.card3_value.configure(text=str(stats["total_routes"]))
            
        except Exception as e:
            print(f"Error loading stats: {e}")
            self.card1_value.configure(text="0")
            self.card2_value.configure(text="0")
            self.card3_value.configure(text="0")
            
    def create_widgets(self):
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="School Transport Management System",
            font=("Arial", 30, "bold")
        )
        self.title_label.pack(pady=(40, 10))
        
        # Welcome Label
        self.welcome_label = ctk.CTkLabel(
            self,
            text="Welcome, Admin! Here's your system overview:",
            font=("Arial", 20)
        )
        self.welcome_label.pack(pady=(0, 30))
        
        # Summary Cards Container
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.pack(pady=20, padx=40, fill="x")
        self.summary_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 1: Total Students
        self.card1 = ctk.CTkFrame(self.summary_frame, corner_radius=15)
        self.card1.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")
        self.card1_title = ctk.CTkLabel(self.card1, text="Total Students", font=("Arial", 16))
        self.card1_title.pack(pady=(20, 5))
        self.card1_value = ctk.CTkLabel(self.card1, text="0", font=("Arial", 36, "bold"), text_color="#1f538d")
        self.card1_value.pack(pady=(0, 20))

        # Card 2: Active Buses
        self.card2 = ctk.CTkFrame(self.summary_frame, corner_radius=15)
        self.card2.grid(row=0, column=1, padx=15, pady=10, sticky="nsew")
        self.card2_title = ctk.CTkLabel(self.card2, text="Active Buses", font=("Arial", 16))
        self.card2_title.pack(pady=(20, 5))
        self.card2_value = ctk.CTkLabel(self.card2, text="0", font=("Arial", 36, "bold"), text_color="#1f538d")
        self.card2_value.pack(pady=(0, 20))

        # Card 3: Total Routes
        self.card3 = ctk.CTkFrame(self.summary_frame, corner_radius=15)
        self.card3.grid(row=0, column=2, padx=15, pady=10, sticky="nsew")
        self.card3_title = ctk.CTkLabel(self.card3, text="Total Routes", font=("Arial", 16))
        self.card3_title.pack(pady=(20, 5))
        self.card3_value = ctk.CTkLabel(self.card3, text="0", font=("Arial", 36, "bold"), text_color="#1f538d")
        self.card3_value.pack(pady=(0, 20))
        
        # Quick Actions Title
        self.quick_actions_label = ctk.CTkLabel(
            self,
            text="Quick Actions",
            font=("Arial", 20, "bold")
        )
        self.quick_actions_label.pack(pady=(30, 10))

        # Quick Actions Container
        self.quick_actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quick_actions_frame.pack(pady=10, padx=40)

        # Shortcut Buttons
        self.btn_add_student = ctk.CTkButton(self.quick_actions_frame, text="Add New Student", command=self.app_controller.open_student_management)
        self.btn_add_student.grid(row=0, column=0, padx=10, pady=10)

        self.btn_view_students = ctk.CTkButton(self.quick_actions_frame, text="View Students", command=self.app_controller.open_student_records)
        self.btn_view_students.grid(row=0, column=1, padx=10, pady=10)

        self.btn_add_bus = ctk.CTkButton(self.quick_actions_frame, text="Manage Buses", command=self.app_controller.open_bus_management)
        self.btn_add_bus.grid(row=0, column=2, padx=10, pady=10)

        self.btn_view_routes = ctk.CTkButton(self.quick_actions_frame, text="View Routes", command=self.app_controller.open_route_records)
        self.btn_view_routes.grid(row=0, column=3, padx=10, pady=10)

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
        self.show_frame(DashboardHome)
        
    def on_close(self):
        if self.master:
            self.master.destroy()
        else:
            self.window.destroy()
            
    def show_frame(self, frame_class):
        # Destroy current content in content_frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if frame_class == DashboardHome:
            frame = DashboardHome(self.content_frame, self)
        else:
            frame = frame_class(self.content_frame)
            
        frame.pack(fill="both", expand=True)
            
    def create_widgets(self):
        
        # Sidebar (Hidden by default)
        self.sidebar_frame = ctk.CTkFrame(
            self.window, 
            width=200, 
            corner_radius=0
        )
        
        # Close Sidebar Button
        self.close_sidebar_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="×",
            width=30,
            height=30,
            command=self.toggle_sidebar,
            font=("Arial", 20, "bold"),
            fg_color="transparent",
            text_color=("black", "white"),
            hover_color=("gray70", "gray30")
        )
        self.close_sidebar_btn.pack(anchor="ne", padx=5, pady=5)

        # Sidebar Title
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_frame,
            text="STMS",
            font=("Arial", 24, "bold")
        )
        self.sidebar_title.pack(pady=(0, 20))
        
        # Main Container
        self.main_container = ctk.CTkFrame(
            self.window,
            corner_radius=0
        )
        self.main_container.pack(
            side="right",
            fill="both",
            expand=True
        )
        
        # Top Bar (for toggle button)
        self.top_bar = ctk.CTkFrame(self.main_container, height=50, corner_radius=0, fg_color="transparent")
        self.top_bar.pack(side="top", fill="x")
        
        # Toggle Sidebar Button
        self.toggle_button = ctk.CTkButton(
            self.top_bar,
            text="☰",
            width=40,
            height=40,
            command=self.toggle_sidebar,
            font=("Arial", 24),
            fg_color="transparent",
            text_color=("black", "white"),
            hover_color=("gray70", "gray30")
        )
        self.toggle_button.pack(anchor="nw", padx=10, pady=10)
        
        # Content Frame
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.content_frame.pack(side="top", fill="both", expand=True)
        
        # Dashboard Button
        self.dashboard_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Dashboard",
            width=170,
            command=lambda: self.show_frame(DashboardHome)
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
        # Logout Button
        self.logout_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Logout",
            width=170,
            command=self.logout
        )
        self.logout_button.pack(pady=10)
        
    def open_student_management(self):
        self.show_frame(StudentManagement)
        
    def open_student_records(self):
        self.show_frame(StudentRecords)
        
    def open_parent_management(self):
        self.show_frame(ParentManagement)
        
    def open_parent_records(self):
        self.show_frame(ParentRecords)
        
    def open_bus_management(self):
        self.show_frame(BusManagement)
        
    def open_route_management(self):
        self.show_frame(RouteManagement)
        
    def open_route_records(self):
        self.show_frame(RouteRecords)
        
    def toggle_sidebar(self):
        if self.sidebar_frame.winfo_ismapped():
            self.sidebar_frame.pack_forget()
        else:
            self.sidebar_frame.pack(side="left", fill="y", before=self.main_container)

    def logout(self):
        self.window.destroy()
        if self.master:
            self.master.deiconify()

    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()
        