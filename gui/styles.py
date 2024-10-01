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
