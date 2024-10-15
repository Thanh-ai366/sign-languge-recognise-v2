import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
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
        self.user = user  # Lưu trữ đối tượng người dùng
        self.setWindowTitle("Hệ thống nhận diện ngôn ngữ ký hiệu")
        self.setGeometry(200, 200, 800, 600)

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

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Khởi động Flask dashboard trong luồng riêng
        self.start_dashboard_thread()

        # Mở Flask dashboard khi khởi tạo MainUI
        self.open_dashboard_window()

    def start_dashboard_thread(self):
        """Khởi động Flask dashboard trong luồng riêng"""
        threading.Thread(target=self.run_dashboard_app).start()

    def run_dashboard_app(self):
        """Chạy Flask dashboard"""
        try:
            dashboard_app.run(debug=True, use_reloader=False)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi động dashboard: {str(e)}")

    def open_dashboard_window(self):
        """Mở cửa sổ Dashboard trong PyQt"""
        self.dashboard_window = QMainWindow()
        self.dashboard_window.setWindowTitle("Dashboard")
        self.dashboard_window.setGeometry(100, 100, 1200, 800)

        web_view = QWebEngineView()
        web_view.setUrl(QUrl("http://127.0.0.1:5000/dashboard"))

        self.dashboard_window.setCentralWidget(web_view)
        self.dashboard_window.show()

    def open_prediction_window(self):
        """Mở cửa sổ Dự đoán"""
        try:
            self.prediction_window = PredictionWindow(self)
            self.prediction_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở cửa sổ Dự đoán: {str(e)}")

    def open_learning_window(self):
        """Mở cửa sổ Học Ngôn ngữ Ký hiệu"""
        try:
            if self.user and hasattr(self.user, 'username'):
                self.learning_window = LearningApp(self.user.username)  # Truyền username vào LearningApp
                self.learning_window.show()
            else:
                QMessageBox.critical(self, "Lỗi", "Người dùng chưa đăng nhập hoặc không có tên đăng nhập.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở cửa sổ Học Ngôn ngữ Ký hiệu: {str(e)}")

    def open_analytics_window(self):
        """Mở cửa sổ Phân tích Dữ liệu"""
        try:
            self.analytics_window = AnalysisWindow()
            self.analytics_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở cửa sổ Phân tích Dữ liệu: {str(e)}")


def handle_login_response(response, login_window):
    """Xử lý kết quả đăng nhập"""
    if "Token:" in response:
        user_manager = UserManager()
        user = user_manager.get_user_from_token(response)  # Lấy thông tin người dùng từ token
        main_ui = MainUI(user)  # Truyền đối tượng người dùng vào MainUI
        main_ui.show()
        login_window.close()
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
