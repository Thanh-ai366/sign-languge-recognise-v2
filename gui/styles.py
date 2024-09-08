# Định nghĩa màu sắc
BG_COLOR = "#F0F8FF"
BUTTON_COLOR = "#00BFFF"
BUTTON_HOVER_COLOR = "#1E90FF"
BUTTON_TEXT_COLOR = "#FFFFFF"
TEXT_COLOR = "#000000"
FONT = ("Arial", 12)
HEADER_FONT = ("Arial", 16, "bold")

def apply_styles(widget, style):
    for key, value in style.items():
        widget[key] = value

def on_hover(event, widget):
    widget["bg"] = BUTTON_HOVER_COLOR

def on_leave(event, widget):
    widget["bg"] = BUTTON_COLOR
