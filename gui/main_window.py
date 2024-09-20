# main_window.py
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from app.prediction import SignLanguagePredictor
from styles import AppStyles  # Import style từ styles.py

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Giao diện dự đoán ký hiệu')
        self.setGeometry(100, 100, 800, 600)

        # Áp dụng style sheet
        self.setStyleSheet(AppStyles.main_window)

        layout = QVBoxLayout()

        # Tạo nhãn tiêu đề
        self.label = QLabel('Dự đoán ký hiệu ngôn ngữ', self)
        layout.addWidget(self.label)

        # Nút bắt đầu dự đoán
        self.start_button = QPushButton('Bắt đầu dự đoán', self)
        self.start_button.clicked.connect(self.start_prediction)
        layout.addWidget(self.start_button)

        # Nút dừng dự đoán
        self.stop_button = QPushButton('Dừng dự đoán', self)
        self.stop_button.setEnabled(False)  # Vô hiệu hóa nút dừng ban đầu
        self.stop_button.clicked.connect(self.stop_prediction)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def start_prediction(self):
        self.predictor = SignLanguagePredictor()
        self.predictor.run()
        
        # Cập nhật giao diện
        self.label.setText("Đang dự đoán...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_prediction(self):
        self.predictor.stop()

        # Cập nhật giao diện
        self.label.setText("Dự đoán đã dừng.")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
