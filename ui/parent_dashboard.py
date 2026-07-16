import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class ParentDashboard:
    
    def __init__(self, parent_id, master=None):
        self.parent_id = parent_id
        self.master = master
        if master is None:
            self.window = ctk.CTk()
        else:
            self.window = ctk.CTkToplevel(master)
            self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.window.title("Parent Dashboard")
        self.window.geometry("900x600")
        self.window.resizable(False, False)
        
        self.fetch_data()
        self.create_widgets()
        
    def on_close(self):
        if self.master:
            self.master.destroy()
        else:
            self.window.destroy()

    def fetch_data(self):
        connection = connect_database()
        cursor = connection.cursor()
        
        # Fetch parent name
        cursor.execute("SELECT parent_name FROM parent WHERE parent_id = ?", (self.parent_id,))
        result = cursor.fetchone()
        self.parent_name = result[0] if result else "Parent"

        # Fetch children info
        cursor.execute("""
            SELECT s.student_name, s.student_class, b.bus_number, b.driver_name, b.driver_phone, 
                   r.route_name, s.fee_status, p.pickup_point
            FROM student s
            JOIN parent p ON s.parent_id = p.parent_id
            LEFT JOIN route r ON s.route_id = r.route_id
            LEFT JOIN bus b ON r.route_id = b.route_id
            WHERE s.parent_id = ?
        """, (self.parent_id,))
        self.children_records = cursor.fetchall()
        connection.close()

    def create_widgets(self):
        # Header Frame
        self.header_frame = ctk.CTkFrame(self.window, corner_radius=0, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=20, padx=20)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=f"Welcome, {self.parent_name}",
            font=("Arial", 28, "bold")
        )
        self.title_label.pack(side="left")
        
        self.logout_button = ctk.CTkButton(
            self.header_frame,
            text="Logout",
            command=self.logout,
            width=100
        )
        self.logout_button.pack(side="right")
        
        # Content Frame (Scrollable to accommodate multiple kids)
        self.content_frame = ctk.CTkScrollableFrame(self.window, width=850, height=480)
        self.content_frame.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkLabel(
            self.content_frame, 
            text="Your Children's Transport Details", 
            font=("Arial", 20, "bold")
        ).pack(pady=(0, 20))

        if not self.children_records:
            ctk.CTkLabel(
                self.content_frame,
                text="No records found for your children.",
                font=("Arial", 16)
            ).pack(pady=20)
        else:
            for child in self.children_records:
                self.create_child_card(child)

    def create_child_card(self, child):
        s_name, s_class, bus_no, drv_name, drv_phone, r_name, fee, p_pickup = child
        
        card = ctk.CTkFrame(self.content_frame, corner_radius=10)
        card.pack(fill="x", pady=10, padx=10, ipadx=10, ipady=10)

        # Child Header
        header_label = ctk.CTkLabel(
            card,
            text=f"{s_name} (Class {s_class})",
            font=("Arial", 18, "bold")
        )
        header_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Fee Status
        fee_color = "green" if fee and fee.lower() == "paid" else "red"
        fee_label = ctk.CTkLabel(
            card,
            text=f"Fee Status: {fee}",
            font=("Arial", 16, "bold"),
            text_color=fee_color
        )
        fee_label.grid(row=0, column=1, sticky="e", pady=(0, 10), padx=20)

        # Bus Details
        bus_frame = ctk.CTkFrame(card, fg_color="transparent")
        bus_frame.grid(row=1, column=0, sticky="w", pady=5)
        
        ctk.CTkLabel(bus_frame, text="Bus Details:", font=("Arial", 16, "underline")).pack(anchor="w")
        ctk.CTkLabel(bus_frame, text=f"Bus Number: {bus_no if bus_no else 'N/A'}", font=("Arial", 14)).pack(anchor="w")
        ctk.CTkLabel(bus_frame, text=f"Driver: {drv_name if drv_name else 'N/A'}", font=("Arial", 14)).pack(anchor="w")
        ctk.CTkLabel(bus_frame, text=f"Contact: {drv_phone if drv_phone else 'N/A'}", font=("Arial", 14)).pack(anchor="w")

        # Route Details
        route_frame = ctk.CTkFrame(card, fg_color="transparent")
        route_frame.grid(row=1, column=1, sticky="nw", pady=5, padx=20)

        ctk.CTkLabel(route_frame, text="Route Details:", font=("Arial", 16, "underline")).pack(anchor="w")
        ctk.CTkLabel(route_frame, text=f"Route: {r_name if r_name else 'N/A'}", font=("Arial", 14)).pack(anchor="w")
        ctk.CTkLabel(route_frame, text=f"Pickup/Drop: {p_pickup if p_pickup else 'N/A'}", font=("Arial", 14)).pack(anchor="w")
        
        # Configure columns to distribute space evenly
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

    def logout(self):
        self.window.destroy()
        if self.master:
            self.master.deiconify()

    def run(self):
        if not isinstance(self.window, ctk.CTkToplevel):
            self.window.mainloop()
