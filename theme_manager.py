import os
import json
from PyQt6.QtWidgets import QApplication, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

def apply_shadow(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(25)
    shadow.setColor(QColor(0, 0, 0, 20))
    shadow.setOffset(0, 5)
    widget.setGraphicsEffect(shadow)

class ThemeManager:
    _instance = None
    _config_file = "theme_config.json"
    
    def __init__(self):
        self.current_theme = "light"
        self.user_type = None
        self.user_id = None
        self.load_preference()
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def set_user(self, user_type: str, user_id: int):
        from dal import db_dal
        self.user_type = user_type
        self.user_id = user_id
        
        user_settings = db_dal.get_user_settings(user_type, user_id)
        if "theme" in user_settings:
            self.current_theme = user_settings["theme"]
            self.apply_theme()

    def load_preference(self):
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    data = json.load(f)
                    self.current_theme = data.get("theme", "light")
        except Exception:
            pass

    def save_preference(self):
        if self.user_type and self.user_id:
            from dal import db_dal
            db_dal.set_user_setting(self.user_type, self.user_id, "theme", self.current_theme)
        else:
            try:
                with open(self._config_file, 'w') as f:
                    json.dump({"theme": self.current_theme}, f)
            except Exception:
                pass

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.save_preference()
        self.apply_theme()
        return self.current_theme

    def apply_theme(self):
        app = QApplication.instance()
        if not app:
            return
            
        theme_file = os.path.join("themes", f"{self.current_theme}.qss")
        theme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), theme_file)
        
        try:
            # Explicitly unset stylesheet before applying new one to prevent stale styles
            app.setStyleSheet("")
            with open(theme_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()
                app.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error applying theme {theme_file}: {e}")

    def get_current_theme(self):
        return self.current_theme
