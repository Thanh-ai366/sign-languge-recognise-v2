import unittest
import tkinter as tk
import time
from gui.main_window import create_main_window

class TestGUIPerformance(unittest.TestCase):
    def test_window_loading_time(self):
        start_time = time.time()
        root = tk.Tk()
        root.update()
        end_time = time.time()

        loading_time = end_time - start_time
        print(f"Thời gian mở cửa sổ GUI: {loading_time:.2f} giây.")
        
        # Đảm bảo rằng cửa sổ được mở trong khoảng thời gian hợp lý (ví dụ dưới 1 giây)
        self.assertLess(loading_time, 1, "Cửa sổ GUI mở quá chậm.")

    def test_button_click_performance(self):
        root = tk.Tk()
        button = tk.Button(root, text="Click me!")
        button.pack()
        root.update()

        # Đo thời gian để click nút
        start_time = time.time()
        button.invoke()
        end_time = time.time()

        click_time = end_time - start_time
        print(f"Thời gian xử lý sau khi click nút: {click_time:.4f} giây.")

        # Đảm bảo rằng phản hồi sau khi click nhanh chóng (ví dụ dưới 0.1 giây)
        self.assertLess(click_time, 0.1, "Phản hồi nút quá chậm.")

if __name__ == '__main__':
    unittest.main()
