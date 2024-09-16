import tkinter as tk
from tkinter import messagebox
import pyttsx3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.prediction import SignLanguagePredictor
from auth.register import Register  # Sử dụng Register cho đăng ký
from auth.login import UserManager  # Sử dụng UserManager cho đăng nhập
from auth.user_data import UserData

def set_tts_options(engine):
    # Tùy chỉnh tốc độ phát âm
    speed = tk.IntVar(value=150)  # Tốc độ mặc định
    tk.Label(root, text="Tốc độ phát âm").pack()
    tk.Scale(root, from_=100, to=300, orient=tk.HORIZONTAL, variable=speed).pack()

    # Tùy chỉnh ngôn ngữ
    language_var = tk.StringVar(value='vi')  # Ngôn ngữ mặc định là tiếng Việt
    tk.Label(root, text="Ngôn ngữ phát âm").pack()
    tk.OptionMenu(root, language_var, 'vi', 'en').pack()

    # Áp dụng các tùy chọn cho engine TTS
    def apply_tts_settings():
        engine.setProperty('rate', speed.get())
        if language_var.get() == 'en':
            engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')  # Ví dụ cho tiếng Anh
        else:
            engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Yuna')  # Ví dụ cho tiếng Việt
    
    apply_tts_settings()

def start_prediction():
    model_path = "data/saved_models/cnn_model.h5"

    # Ánh xạ lại nhãn: 0-9 cho số, 10-35 cho ký tự a-z
    labels_dict = {i: str(i) for i in range(10)}
    labels_dict.update({10 + i: chr(97 + i) for i in range(26)})  # 10 -> 'a', 35 -> 'z'

    predictor = SignLanguagePredictor(model_path, labels_dict)
    predictor.run()

def on_closing():
    if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát không?"):
        root.destroy()

def login():
    username = username_entry.get()
    password = password_entry.get()
    user_manager = UserManager()  # Sử dụng UserManager cho đăng nhập
    response = user_manager.login(username, password)
    if "Token:" in response:
        token = response.split("Token: ")[1]
        user_data = UserData(username)
        start_prediction()
    else:
        messagebox.showerror("Đăng nhập thất bại", response)

def open_register_window():
    # Tạo cửa sổ đăng ký
    register_window = tk.Toplevel(root)
    register_window.title("Đăng Ký")
    register_window.geometry("300x200")

    tk.Label(register_window, text="Tên người dùng (Đăng ký)").pack()
    register_username_entry = tk.Entry(register_window)
    register_username_entry.pack()

    tk.Label(register_window, text="Mật khẩu (Đăng ký)").pack()
    register_password_entry = tk.Entry(register_window, show="*")
    register_password_entry.pack()

    def register():
        username = register_username_entry.get()
        password = register_password_entry.get()
        user_manager = Register()  # Sử dụng Register cho đăng ký
        response = user_manager.register(username, password)
        messagebox.showinfo("Đăng ký", response)
        register_window.destroy()

    register_button = tk.Button(register_window, text="Đăng ký", command=register)
    register_button.pack(pady=20)

root = tk.Tk()
root.title("Phần Mềm Nhận Diện Ngôn Ngữ Ký Hiệu")
root.geometry("400x600")  # Tăng kích thước cửa sổ để thêm UI cho đăng ký

# Khởi tạo engine TTS và cấu hình
engine = pyttsx3.init()
set_tts_options(engine)

# Giao diện đăng nhập
tk.Label(root, text="Tên người dùng").pack()
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Mật khẩu").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

login_button = tk.Button(root, text="Đăng nhập", command=login)
login_button.pack(pady=20)

# Thêm nút để mở cửa sổ đăng ký
register_button = tk.Button(root, text="Đăng ký", command=open_register_window)
register_button.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
