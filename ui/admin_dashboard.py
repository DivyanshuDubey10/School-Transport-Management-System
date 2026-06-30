import customtkinter as ctk

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
            side="Left", 
            fill="y"
        )
        
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
        
    def run(self):
        self.window.mainloop()
        