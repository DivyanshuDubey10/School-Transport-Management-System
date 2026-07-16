import customtkinter as ctk
import json

with open('default_theme.json', 'w', encoding='utf-8') as f:
    json.dump(ctk.ThemeManager.theme, f, indent=4)
