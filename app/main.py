import tkinter as tk
from tkinter import messagebox
import pyttsx3
import sys
import os
import threading
from dotenv import load_dotenv
from app.prediction import SignLanguagePredictor
from auth.register import Register
from auth.login import UserManager
from auth.user_data import UserData

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def set_tts_options(engine):
    speed = tk.IntVar(value=150)  # Tốc độ mặc định
    tk.Label(root, text="Tốc độ phát âm").pack()
    speed_scale = tk.Scale(root, from_=100, to=300, orient=tk.HORIZONTAL, variable=speed)
    speed_scale.pack()
    
    language_var = tk.StringVar(value='vi')  # Ngôn ngữ mặc định là tiếng Việt
    tk.Label(root, text="Ngôn ngữ phát âm").pack()
    language_menu = tk.OptionMenu(root, language_var, 'vi', 'en')
    language_menu.pack()

    def apply_tts_settings():
        engine.setProperty('rate', speed.get())
        if language_var.get() == 'en':
            engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')  # Tiếng Anh
        else:
            engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Yuna')  # Tiếng Việt

    speed.trace_add("write", lambda *args: apply_tts_settings())
    language_var.trace_add("write", lambda *args: apply_tts_settings())

def start_prediction():
    model_path = "app/data/saved_models/cnn_model.h5"
    labels_dict = {i: str(i) for i in range(10)}
    labels_dict.update({10 + i: chr(97 + i) for i in range(26)})
    predictor = SignLanguagePredictor(model_path, labels_dict)
    predictor.run()

def on_closing():
    if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát không?"):
        root.destroy()

def login():
    def authenticate():
        username = username_entry.get()
        password = password_entry.get()
        user_manager = UserManager()
        response = user_manager.login(username, password)
        loading_spinner.pack_forget()
        if "Token:" in response:
            user_data = UserData(username)
            start_prediction()
        else:
            messagebox.showerror("Đăng nhập thất bại", response)
    
    # Hiển thị loading spinner khi đang xác thực
    loading_spinner.pack()
    threading.Thread(target=authenticate).start()

def open_register_window():
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
        user_manager = Register()
        response = user_manager.register(username, password)
        messagebox.showinfo("Đăng ký", response)
        register_window.destroy()

    register_button = tk.Button(register_window, text="Đăng ký", command=register)
    register_button.pack(pady=20)

root = tk.Tk()
root.title("Phần Mềm Nhận Diện Ngôn Ngữ Ký Hiệu")
root.geometry("400x600")

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

# Thêm loading spinner khi xác thực
loading_spinner = tk.Label(root, text="Đang xử lý...")
loading_spinner.pack_forget()

register_button = tk.Button(root, text="Đăng ký", command=open_register_window)
register_button.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
