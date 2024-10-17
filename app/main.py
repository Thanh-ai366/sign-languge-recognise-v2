import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox, QStackedWidget
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
        self.user = user
        self.setWindowTitle("Ngôn ngữ Ký hiệu - Giao diện chính")
        self.setGeometry(200, 200, 1000, 800)

        # QStackedWidget chứa các màn hình chức năng
        self.stacked_widget = QStackedWidget()
        
        # Khởi tạo các màn hình chức năng
        self.prediction_window = PredictionWindow(self)
        self.learning_window = LearningApp(self.user.username)
        self.analytics_window = AnalysisWindow()

        # Thêm các màn hình vào stacked_widget
        self.stacked_widget.addWidget(self.prediction_window)
        self.stacked_widget.addWidget(self.learning_window)
        self.stacked_widget.addWidget(self.analytics_window)

        # Nút quay lại
        self.back_button = QPushButton("Quay lại")
        self.back_button.clicked.connect(self.go_back)

        # Nút chuyển đổi chế độ sáng/tối
        self.mode_button = QPushButton("Chuyển chế độ sáng/tối")
        self.mode_button.clicked.connect(self.toggle_mode)

        # Layout chính
        layout = QVBoxLayout()
        layout.addWidget(self.back_button)
        layout.addWidget(self.mode_button)
        layout.addWidget(self.stacked_widget)

        # Tạo container cho layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.start_dashboard_thread()

        self.open_dashboard_window()
    def go_back(self):
        """Quay lại màn hình chính (Dashboard)"""
        self.stacked_widget.setCurrentIndex(0)

    def toggle_mode(self):
        """Chuyển đổi giữa chế độ sáng và tối"""
        pass


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
    if "Token:" in response and "Refresh Token:" in response:
        user_manager = UserManager()
        token = response.split("Token: ")[1].strip()  # Lấy token từ phản hồi
        refresh_token = response.split("Refresh Token: ")[1].strip()  # Lấy refresh token từ phản hồi
        try:
            user_manager.get_user_from_token(token)  # Lấy thông tin người dùng từ token
            user_manager.open_main_app(token, refresh_token)  # Mở MainApp với token và refresh_token
            login_window.close()
        except ValueError as e:
            QMessageBox.critical(login_window, 'Lỗi Token', str(e))
    else:
        QMessageBox.critical(login_window, 'Thất bại', response)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_window = LoginWindow()

    login_window.auth_result_signal.connect(lambda response: handle_login_response(response, login_window))

    login_window.show()

    sys.exit(app.exec_())
