import unittest
import tkinter as tk
from gui.main_window import create_main_window

class TestGUI(unittest.TestCase):
    def test_window_creation(self):
        root = tk.Tk()
        self.assertIsNotNone(root, "Không thể tạo cửa sổ giao diện.")

    def test_main_window_function(self):
        try:
            create_main_window()
        except Exception as e:
            self.fail(f"Khởi chạy giao diện thất bại với lỗi: {e}")

if __name__ == '__main__':
    unittest.main()
