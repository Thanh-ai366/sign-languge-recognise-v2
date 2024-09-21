from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
from app.prediction import SignLanguagePredictor
from styles import AppStyles

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Giao diện dự đoán ký hiệu')
        self.setGeometry(100, 100, 800, 600)
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
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_prediction)
        layout.addWidget(self.stop_button)

        # Nút trợ giúp
        self.help_button = QPushButton('Trợ giúp', self)
        self.help_button.clicked.connect(self.show_help)
        layout.addWidget(self.help_button)

        self.setLayout(layout)

    def start_prediction(self):
        try:
            self.predictor = SignLanguagePredictor("app/data/saved_models/cnn_model.h5", {i: str(i) for i in range(36)})
            self.predictor.run()

            self.label.setText("Đang dự đoán...")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        except Exception as e:
            self.show_error(str(e))
            self.start_button.setEnabled(True)

    def stop_prediction(self):
        if hasattr(self, 'predictor') and self.predictor is not None:
            self.predictor.running = False
            self.label.setText("Dự đoán đã dừng.")
        else:
            self.label.setText("Không có quá trình dự đoán để dừng.")
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def show_help(self):
        QMessageBox.information(self, 'Trợ giúp', 'Hướng dẫn sử dụng phần mềm nhận diện ký hiệu ngôn ngữ...')

    def show_error(self, error_message):
        QMessageBox.critical(self, 'Lỗi', f"Đã xảy ra lỗi: {error_message}")
