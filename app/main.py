import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox, QStackedWidget, QLabel
)
from PyQt5.QtWebEngineWidgets import QWebEngineView 
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QMovie, QFont 
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

        self.is_dark_mode = False  # Biến để theo dõi trạng thái sáng/tối

        # QStackedWidget chứa các màn hình chức năng
        self.stacked_widget = QStackedWidget()

        # Khởi tạo màn hình dashboard trước (các cửa sổ chức năng khác sẽ chỉ được khởi tạo khi cần)
        self.stacked_widget.addWidget(QWidget())  # Trang trống ban đầu hoặc trang dashboard

        # Nhãn "SLR" làm tên sản phẩm ở trên cùng
        self.title_label = QLabel("SLR")
        self.title_label.setFont(QFont('Arial', 36, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        # Ảnh động (GIF) hiển thị ở giữa màn hình
        self.gif_label = QLabel(self)
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.movie = QMovie("path_to_your_gif.gif")  # Thay bằng đường dẫn tới ảnh GIF của bạn
        self.gif_label.setMovie(self.movie)
        self.movie.start()

        # Nút quay lại
        self.back_button = QPushButton("Quay lại")
        self.back_button.clicked.connect(self.go_back)

        # Nút chuyển đổi chế độ sáng/tối, nằm ở góc trên bên phải
        self.mode_button = QPushButton("Chuyển chế độ sáng/tối")
        self.mode_button.clicked.connect(self.toggle_mode)
        self.mode_button.setFixedSize(150, 40)

        # Nút mở các cửa sổ chức năng, căn giữa màn hình với kích thước thích hợp
        self.prediction_button = QPushButton("Mở Dự đoán")
        self.prediction_button.setFixedSize(250, 100)
        self.prediction_button.clicked.connect(self.open_prediction_window)

        self.learning_button = QPushButton("Mở Học Ngôn ngữ Ký hiệu")
        self.learning_button.setFixedSize(250, 100)
        self.learning_button.clicked.connect(self.open_learning_window)

        self.analytics_button = QPushButton("Mở Phân tích Dữ liệu")
        self.analytics_button.setFixedSize(250, 100)
        self.analytics_button.clicked.connect(self.open_analytics_window)

        # Layout cho các nút chính
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.prediction_button)
        button_layout.addWidget(self.learning_button)
        button_layout.addWidget(self.analytics_button)
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(20)

        # Layout chính
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)        # Nhãn "SLR" ở trên cùng
        main_layout.addWidget(self.gif_label)          # Ảnh động ở giữa
        main_layout.addLayout(button_layout)           # Các nút chức năng ở giữa
        main_layout.addStretch()

        # Tạo container cho layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Nút chuyển chế độ sáng/tối được đặt vào góc phải
        self.mode_button.setParent(self)
        self.mode_button.move(self.width() - self.mode_button.width() - 20, 20)

        self.start_dashboard_thread()
        self.open_dashboard_window()

        # Biến giữ các cửa sổ chức năng, khởi tạo sau khi bấm nút
        self.prediction_window = None
        self.learning_window = None
        self.analytics_window = None

    def resizeEvent(self, event):
        """Cập nhật vị trí nút chuyển đổi chế độ sáng/tối khi thay đổi kích thước cửa sổ"""
        self.mode_button.move(self.width() - self.mode_button.width() - 20, 20)

    def go_back(self):
        """Quay lại màn hình chính (Dashboard)"""
        self.stacked_widget.setCurrentIndex(0)

    def toggle_mode(self):
        """Chuyển đổi giữa chế độ sáng và tối"""
        if self.is_dark_mode:
            self.setStyleSheet("")  # Trở về chế độ sáng
            self.prediction_button.setStyleSheet("background-color: #4CAF50; color: white;")
            self.learning_button.setStyleSheet("background-color: #2196F3; color: white;")
            self.analytics_button.setStyleSheet("background-color: #FF5722; color: white;")
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #555555;
                    color: #ffffff;
                    border: 1px solid #888888;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
            """)  # Chế độ tối
        self.is_dark_mode = not self.is_dark_mode  # Đảo trạng thái sáng/tối

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

    def close_other_windows(self):
        """Ẩn tất cả các cửa sổ hiện tại"""
        if self.prediction_window:
            self.prediction_window.hide()
        if self.learning_window:
            self.learning_window.hide()
        if self.analytics_window:
            self.analytics_window.hide()

    def open_prediction_window(self):
        """Mở cửa sổ Dự đoán, khởi tạo nếu chưa tồn tại"""
        try:
            if not self.prediction_window:
                self.prediction_window = PredictionWindow(self)
                self.stacked_widget.addWidget(self.prediction_window)

            self.close_other_windows()  # Đóng các cửa sổ khác trước khi mở
            self.stacked_widget.setCurrentWidget(self.prediction_window)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở cửa sổ Dự đoán: {str(e)}")

    def open_learning_window(self):
        """Mở cửa sổ Học Ngôn ngữ Ký hiệu, khởi tạo nếu chưa tồn tại"""
        try:
            if not self.learning_window and self.user and hasattr(self.user, 'username'):
                self.learning_window = LearningApp(self.user.username)
                self.stacked_widget.addWidget(self.learning_window)

            self.close_other_windows()  # Đóng các cửa sổ khác trước khi mở
            self.stacked_widget.setCurrentWidget(self.learning_window)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở cửa sổ Học Ngôn ngữ Ký hiệu: {str(e)}")

    def open_analytics_window(self):
        """Mở cửa sổ Phân tích Dữ liệu, khởi tạo nếu chưa tồn tại"""
        try:
            if not self.analytics_window:
                self.analytics_window = AnalysisWindow()
                self.stacked_widget.addWidget(self.analytics_window)

            self.close_other_windows()  # Đóng các cửa sổ khác trước khi mở
            self.stacked_widget.setCurrentWidget(self.analytics_window)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở cửa sổ Phân tích Dữ liệu: {str(e)}")

def handle_login_response(response, login_window):
    """Xử lý kết quả đăng nhập"""
    if isinstance(response, dict) and "token" in response and "refresh_token" in response:
        user_manager = UserManager()
        token = response["token"]  # Lấy token từ phản hồi
        refresh_token = response["refresh_token"]  # Lấy refresh token từ phản hồi
        try:
            user = user_manager.get_user_from_token(token)  # Lấy thông tin người dùng từ token
            if user:
                main_app = MainUI(user)  # Mở MainApp với thông tin người dùng
                main_app.show()  # Hiển thị ứng dụng chính
                login_window.close()  # Đóng cửa sổ đăng nhập
            else:
                QMessageBox.critical(login_window, 'Lỗi', 'Không tìm thấy thông tin người dùng.')
        except ValueError as e:
            QMessageBox.critical(login_window, 'Lỗi Token', str(e))
    else:
        QMessageBox.critical(login_window, 'Thất bại', "Đăng nhập thất bại, vui lòng thử lại.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_window = LoginWindow()

    login_window.auth_result_signal.connect(lambda response: handle_login_response(response, login_window))

    login_window.show()

    sys.exit(app.exec_())
