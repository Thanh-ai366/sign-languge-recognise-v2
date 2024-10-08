import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from flask import Flask, render_template
from prediction import PredictionWindow
from learning import LearningApp
from analytics import AnalysisWindow
from user_manager import LoginWindow, UserManager

# Khởi tạo ứng dụng Flask cho dashboard
dashboard_app = Flask(__name__)

@dashboard_app.route('/dashboard')
def dashboard():
    # Hiển thị dashboard
    return render_template('dashboard.html')

class MainUI(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Hệ thống nhận diện ngôn ngữ ký hiệu")
        self.setGeometry(200, 200, 800, 600)

        # Giao diện chính chứa 3 nút Prediction, Learning, Analytics
        layout = QVBoxLayout()

        # Nút Prediction
        self.prediction_button = QPushButton("Dự đoán Ngôn ngữ Ký hiệu")
        self.prediction_button.clicked.connect(self.open_prediction_window)
        layout.addWidget(self.prediction_button)

        # Nút Learning
        self.learning_button = QPushButton("Học Ngôn ngữ Ký hiệu")
        self.learning_button.clicked.connect(self.open_learning_window)
        layout.addWidget(self.learning_button)

        # Nút Analytics
        self.analytics_button = QPushButton("Phân tích dữ liệu")
        self.analytics_button.clicked.connect(self.open_analytics_window)
        layout.addWidget(self.analytics_button)

        # Thiết lập layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Khởi động dashboard Flask
        self.start_dashboard_thread()

        # Mở dashboard ngay khi khởi tạo MainUI
        self.open_dashboard_window()

    def start_dashboard_thread(self):
        """Khởi động Flask trong luồng riêng"""
        threading.Thread(target=self.run_dashboard_app).start()

    def run_dashboard_app(self):
        dashboard_app.run(debug=True, use_reloader=False)  # Không sử dụng reloader khi chạy trong luồng

    def open_dashboard_window(self):
        """Mở cửa sổ Dashboard trong PyQt"""
        self.dashboard_window = QMainWindow()
        self.dashboard_window.setWindowTitle("Dashboard")
        self.dashboard_window.setGeometry(100, 100, 1200, 800)

        web_view = QWebEngineView()
        web_view.setUrl(QUrl("http://127.0.0.1:5000/dashboard")) 
        Flask
        self.dashboard_window.setCentralWidget(web_view)
        self.dashboard_window.show()

    def open_prediction_window(self):
        """Mở cửa sổ Dự đoán"""
        self.prediction_window = PredictionWindow(self)
        self.prediction_window.show()

    def open_learning_window(self):
        """Mở cửa sổ Học Ngôn ngữ Ký hiệu"""
        self.learning_window = LearningApp(self.user.username)
        self.learning_window.show()

    def open_analytics_window(self):
        """Mở cửa sổ Phân tích Dữ liệu"""
        self.analytics_window = AnalysisWindow()
        self.analytics_window.show()

def handle_login_response(response, login_window):
    if "Token:" in response:
        user_manager = UserManager()
        main_ui = MainUI(user_manager)
        main_ui.show()
        login_window.close()  # Đóng cửa sổ đăng nhập
    else:
        QMessageBox.critical(login_window, 'Thất bại', response)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Hiển thị cửa sổ đăng nhập
    login_window = LoginWindow()

    # Kết nối tín hiệu đăng nhập thành công
    login_window.auth_result_signal.connect(lambda response: handle_login_response(response, login_window))

    login_window.show()

    sys.exit(app.exec_())
