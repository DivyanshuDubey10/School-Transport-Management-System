import customtkinter as ctk
from tkinter import ttk
from ui.login import LoginWindow

def main():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    # Configure global Treeview styling for dark mode
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Treeview",
        background="#2b2b2b",
        foreground="white",
        fieldbackground="#2b2b2b",
        borderwidth=1,
        relief="solid"
    )
    style.map(
        "Treeview",
        background=[("selected", "#1f538d")],
        foreground=[("selected", "white")]
    )
    style.configure(
        "Treeview.Heading",
        background="#333333",
        foreground="white",
        borderwidth=1,
        relief="flat",
        font=("Arial", 10, "bold")
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#4d4d4d")],
        foreground=[("active", "white")]
    )

    app = LoginWindow()
    app.run()
    
if __name__ == "__main__":
    main()