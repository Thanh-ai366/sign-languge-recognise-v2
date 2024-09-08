import tkinter as tk
from gui.styles import BG_COLOR, BUTTON_COLOR, BUTTON_TEXT_COLOR, TEXT_COLOR, FONT, HEADER_FONT, apply_styles, on_hover, on_leave
from app.main import start_prediction, start_reverse_recognition

def create_main_window():
    root = tk.Tk()
    root.title("Phần Mềm Nhận Diện Ngôn Ngữ Ký Hiệu")
    root.geometry("600x400")
    root.configure(bg=BG_COLOR)

    header = tk.Label(root, text="Nhận Diện Ngôn Ngữ Ký Hiệu", fg=TEXT_COLOR, bg=BG_COLOR, font=HEADER_FONT)
    header.pack(pady=20)

    btn_predict = tk.Button(root, text="Nhận Diện Từ Webcam", command=start_prediction)
    apply_styles(btn_predict, {"bg": BUTTON_COLOR, "fg": BUTTON_TEXT_COLOR, "font": FONT})
    btn_predict.bind("<Enter>", lambda event: on_hover(event, btn_predict))
    btn_predict.bind("<Leave>", lambda event: on_leave(event, btn_predict))
    btn_predict.pack(pady=20)

    btn_reverse = tk.Button(root, text="Nhận Diện Từ Giọng Nói", command=start_reverse_recognition)
    apply_styles(btn_reverse, {"bg": BUTTON_COLOR, "fg": BUTTON_TEXT_COLOR, "font": FONT})
    btn_reverse.bind("<Enter>", lambda event: on_hover(event, btn_reverse))
    btn_reverse.bind("<Leave>", lambda event: on_leave(event, btn_reverse))
    btn_reverse.pack(pady=20)

    info_label = tk.Label(root, text="Chọn chức năng bạn muốn thực hiện", fg=TEXT_COLOR, bg=BG_COLOR, font=FONT)
    info_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_main_window()
