# styles.py

class AppStyles:
    main_window = """
        QWidget {
            background-color: #F5F5F5;  /* Màu nền */
        }
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #333;  /* Màu chữ */
        }
        QPushButton {
            background-color: #4CAF50;  /* Màu nền nút */
            color: white;
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;  /* Hiệu ứng hover */
        }
        QPushButton:disabled {
            background-color: #A9A9A9;  /* Màu khi nút bị vô hiệu hóa */
        }
    """
    # CSS cho chế độ sáng
    light_mode = """
        QWidget {
            background-color: #FFFFFF;
            color: #000000;
        }
        QPushButton {
            background-color: #2563EB;
            color: white;
            border-radius: 5px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #1D4ED8;
        }
    """

    # CSS cho chế độ tối
    dark_mode = """
        QWidget {
            background-color: #1F2937;
            color: #F3F4F6;
        }
        QPushButton {
            background-color: #3B82F6;
            color: white;
            border-radius: 5px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #2563EB;
        }
    """

    # Hàm chuyển đổi chế độ trong ứng dụng
    @staticmethod
    def apply_styles(app, dark_mode=False):
        if dark_mode:
            app.setStyleSheet(AppStyles.dark_mode)
        else:
            app.setStyleSheet(AppStyles.light_mode)