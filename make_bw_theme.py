import json

def make_bw():
    with open('default_theme.json', 'r', encoding='utf-8') as f:
        theme = json.load(f)

    # General colors
    bg_color = "#F5F6FA"    # Very light gray background
    frame_color = "#FFFFFF" # Pure white for cards/frames
    black = "#111111"       # Soft black
    dark_gray = "#2B2B2B"   # Button hover
    mid_gray = "#888888"    # Placeholders / disabled
    light_gray = "#E0E0E0"  # Borders
    white = "#FFFFFF"

    # CTk
    theme['CTk']['fg_color'] = [bg_color, bg_color]
    theme['CTkToplevel']['fg_color'] = [bg_color, bg_color]
    
    # Frame
    theme['CTkFrame']['fg_color'] = [frame_color, frame_color]
    theme['CTkFrame']['top_fg_color'] = [frame_color, frame_color]
    theme['CTkFrame']['border_color'] = [light_gray, light_gray]
    theme['CTkFrame']['border_width'] = 1
    theme['CTkFrame']['corner_radius'] = 8

    # Button
    theme['CTkButton']['fg_color'] = [black, black]
    theme['CTkButton']['hover_color'] = [dark_gray, dark_gray]
    theme['CTkButton']['border_color'] = [black, black]
    theme['CTkButton']['text_color'] = [white, white]
    theme['CTkButton']['text_color_disabled'] = [mid_gray, mid_gray]
    theme['CTkButton']['corner_radius'] = 6
    theme['CTkButton']['border_width'] = 0

    # Label
    theme['CTkLabel']['text_color'] = [black, black]
    
    # Entry
    theme['CTkEntry']['fg_color'] = [white, white]
    theme['CTkEntry']['border_color'] = [light_gray, light_gray]
    theme['CTkEntry']['text_color'] = [black, black]
    theme['CTkEntry']['placeholder_text_color'] = [mid_gray, mid_gray]
    theme['CTkEntry']['corner_radius'] = 6
    theme['CTkEntry']['border_width'] = 1

    # CheckBox
    theme['CTkCheckBox']['fg_color'] = [black, black]
    theme['CTkCheckBox']['border_color'] = [light_gray, light_gray]
    theme['CTkCheckBox']['hover_color'] = [dark_gray, dark_gray]
    theme['CTkCheckBox']['checkmark_color'] = [white, white]
    theme['CTkCheckBox']['text_color'] = [black, black]
    theme['CTkCheckBox']['corner_radius'] = 4

    # Switch
    theme['CTkSwitch']['fg_color'] = [light_gray, light_gray]
    theme['CTkSwitch']['progress_color'] = [black, black]
    theme['CTkSwitch']['button_color'] = [white, white]
    theme['CTkSwitch']['button_hover_color'] = [bg_color, bg_color]
    theme['CTkSwitch']['text_color'] = [black, black]

    # RadioButton
    theme['CTkRadioButton']['fg_color'] = [black, black]
    theme['CTkRadioButton']['border_color'] = [light_gray, light_gray]
    theme['CTkRadioButton']['hover_color'] = [dark_gray, dark_gray]
    theme['CTkRadioButton']['text_color'] = [black, black]
    theme['CTkRadioButton']['corner_radius'] = 1000

    # ProgressBar
    theme['CTkProgressBar']['fg_color'] = [light_gray, light_gray]
    theme['CTkProgressBar']['progress_color'] = [black, black]
    theme['CTkProgressBar']['border_color'] = [black, black]
    theme['CTkProgressBar']['corner_radius'] = 4

    # Slider
    theme['CTkSlider']['fg_color'] = [light_gray, light_gray]
    theme['CTkSlider']['progress_color'] = [mid_gray, mid_gray]
    theme['CTkSlider']['button_color'] = [black, black]
    theme['CTkSlider']['button_hover_color'] = [dark_gray, dark_gray]

    # OptionMenu
    theme['CTkOptionMenu']['fg_color'] = [white, white]
    theme['CTkOptionMenu']['button_color'] = [black, black]
    theme['CTkOptionMenu']['button_hover_color'] = [dark_gray, dark_gray]
    theme['CTkOptionMenu']['text_color'] = [black, black]
    theme['CTkOptionMenu']['corner_radius'] = 6

    # ComboBox
    theme['CTkComboBox']['fg_color'] = [white, white]
    theme['CTkComboBox']['border_color'] = [light_gray, light_gray]
    theme['CTkComboBox']['button_color'] = [light_gray, light_gray]
    theme['CTkComboBox']['button_hover_color'] = [mid_gray, mid_gray]
    theme['CTkComboBox']['text_color'] = [black, black]
    theme['CTkComboBox']['corner_radius'] = 6
    theme['CTkComboBox']['border_width'] = 1

    # Scrollbar
    theme['CTkScrollbar']['button_color'] = [mid_gray, mid_gray]
    theme['CTkScrollbar']['button_hover_color'] = [black, black]
    theme['CTkScrollbar']['corner_radius'] = 1000

    # SegmentedButton
    theme['CTkSegmentedButton']['fg_color'] = [white, white]
    theme['CTkSegmentedButton']['selected_color'] = [black, black]
    theme['CTkSegmentedButton']['selected_hover_color'] = [dark_gray, dark_gray]
    theme['CTkSegmentedButton']['unselected_color'] = [white, white]
    theme['CTkSegmentedButton']['unselected_hover_color'] = [bg_color, bg_color]
    theme['CTkSegmentedButton']['text_color'] = [white, white]
    theme['CTkSegmentedButton']['corner_radius'] = 6
    theme['CTkSegmentedButton']['border_width'] = 1

    # Textbox
    theme['CTkTextbox']['fg_color'] = [white, white]
    theme['CTkTextbox']['border_color'] = [light_gray, light_gray]
    theme['CTkTextbox']['text_color'] = [black, black]
    theme['CTkTextbox']['corner_radius'] = 6
    theme['CTkTextbox']['border_width'] = 1

    with open('bw_theme.json', 'w', encoding='utf-8') as f:
        json.dump(theme, f, indent=4)

if __name__ == "__main__":
    make_bw()
