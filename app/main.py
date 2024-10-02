import os
import sys
import threading

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'E:\Anaconda\envs\sign1\Lib\site-packages\PyQt5\Qt5\plugins'

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QStackedWidget, QWidget, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import cv2
import numpy as np
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auth.register import Register
from auth.login import UserManager
from models.model_loader import load_model
from analytics import DataLogger
from learning import Feedback, LessonManager, ProgressTracker
from analytics import SignAnalysis, ReportGenerator
from prediction import SignLanguagePredictor

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


# Lớp PredictionThread để xử lý dự đoán trong luồng riêng biệt
class PredictionThread(QThread):
    prediction_signal = pyqtSignal(str)  # Tín hiệu gửi kết quả dự đoán

    def __init__(self, predictor, parent=None):
        super().__init__(parent)
        self.predictor = predictor  # Đối tượng SignLanguagePredictor để thực hiện dự đoán
        self.running = False  # Cờ để kiểm soát quá trình chạy

    def run(self):
        self.running = True
        count = 0
        result_list = []
        prev_sign = None

        while self.running:
            frame = self.predictor.get_frame()  # Lấy khung hình từ webcam
            if frame is None:
                break

            roi = self.predictor.get_roi(frame)  # Lấy khu vực quan sát
            gray = self.predictor.preprocess_image(roi)  # Xử lý ảnh

            if count < 30:
                self.predictor.run_avg(gray, self.predictor.a_weight)
            else:
                hand = self.predictor.extract_hand(gray)
                if hand is not None:
                    thresh, _ = hand
                    res = cv2.bitwise_and(roi, roi, mask=thresh)
                    res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

                    final_res = self.predictor.preprocess_frame(res)
                    predicted_sign = self.predictor.predict(final_res)

                    # Cập nhật kết quả và gửi tín hiệu về giao diện chính
                    self.update_results(count, predicted_sign, result_list, prev_sign)
                    self.prediction_signal.emit(predicted_sign)

            count += 1

    def update_results(self, count, predicted_sign, result_list, prev_sign):
        if count > 10:
            result_list.append(predicted_sign)
            if count % 50 == 0 and result_list:
                final_sign = max(set(result_list), key=result_list.count)
                if prev_sign != final_sign:
                    return final_sign
        return prev_sign

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class LoginWindow(QWidget):
    auth_result_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.auth_result_signal.connect(self.handle_auth_result)

    def initUI(self):
        self.setWindowTitle('Đăng nhập')
        self.setGeometry(100, 100, 400, 300)
        self.setAutoFillBackground(True)
        
        palette = self.palette()
        background_image = QPixmap("path/to/login_background.jpg")
        palette.setBrush(QPalette.Window, QBrush(background_image.scaled(self.size(),
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)

        layout = QVBoxLayout()
        title = QLabel('Đăng nhập vào hệ thống', self)
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText("Tên người dùng")
        layout.addWidget(self.username_entry)

        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Mật khẩu")
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        self.login_button = QPushButton('Đăng nhập', self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        register_button = QPushButton('Đăng ký', self)
        register_button.clicked.connect(self.open_register_window)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        user_manager = UserManager()
        threading.Thread(target=self.authenticate, args=(user_manager, username, password)).start()

    def authenticate(self, user_manager, username, password):
        response = user_manager.login(username, password)
        self.auth_result_signal.emit(response)

    def handle_auth_result(self, response):
        if "Token:" in response:
            QMessageBox.information(self, 'Đăng nhập thành công', 'Đăng nhập thành công')
            self.open_main_app()
        else:
            QMessageBox.critical(self, 'Đăng nhập thất bại', response)

    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

    def open_main_app(self):
        self.main_app = MainApp()
        self.main_app.show()
        self.close()


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Đăng ký')
        self.setGeometry(150, 150, 300, 200)

        layout = QVBoxLayout()
        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText("Tên người dùng")
        layout.addWidget(self.username_entry)

        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Mật khẩu")
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        register_button = QPushButton('Đăng ký', self)
        register_button.clicked.connect(self.register)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def register(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        user_manager = Register()
        email = "example@example.com"
        response = user_manager.register(username, password, email)
        QMessageBox.information(self, 'Đăng ký', response)
        self.close()


class PredictionScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dự đoán ngôn ngữ ký hiệu")

        # Tạo bộ dự đoán
        self.predictor = SignLanguagePredictor(r"C:\Users\ASUS\Downloads\sign-languge-recognise-v2\app\data\saved_models\cnn_model_best.keras", labels_dict=self.get_labels_dict())
        
        # Tạo luồng dự đoán
        self.prediction_thread = PredictionThread(self.predictor)

        # Nhãn để hiển thị dự đoán
        self.result_label = QLabel("Dự đoán: ")
        self.result_label.setAlignment(Qt.AlignCenter)

        # Nút bắt đầu và dừng dự đoán
        self.start_button = QPushButton("Bắt đầu dự đoán")
        self.stop_button = QPushButton("Dừng dự đoán")

        layout = QVBoxLayout()
        layout.addWidget(self.result_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        # Sự kiện nhấn nút
        self.start_button.clicked.connect(self.start_prediction)
        self.stop_button.clicked.connect(self.stop_prediction)

        # Kết nối tín hiệu từ PredictionThread đến giao diện chính
        self.prediction_thread.prediction_signal.connect(self.update_prediction)

    def start_prediction(self):
        # Bắt đầu luồng dự đoán
        self.prediction_thread.start()

    def stop_prediction(self):
        # Dừng luồng dự đoán
        self.prediction_thread.stop()

    def update_prediction(self, predicted_sign):
        # Cập nhật kết quả dự đoán lên giao diện
        self.result_label.setText(f"Dự đoán: {predicted_sign}")

    def get_labels_dict(self):
        # Tạo từ điển nhãn cho dự đoán
        return {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I',
                9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 
                22: 'W', 23: 'X', 24: 'Y', 25: 'Z'}

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng dụng Ngôn ngữ Ký hiệu")
        self.setGeometry(100, 100, 600, 400)

        # Tạo các nút chức năng
        self.prediction_button = QPushButton("Dự đoán")
        self.learning_button = QPushButton("Học")
        self.analytics_button = QPushButton("Phân tích")

        # Kết nối các nút với các hàm tương ứng
        self.prediction_button.clicked.connect(self.open_prediction_screen)
        self.learning_button.clicked.connect(self.open_learning_screen)
        self.analytics_button.clicked.connect(self.open_analytics_screen)

        # Tạo layout cho màn hình chính
        layout = QVBoxLayout()
        layout.addWidget(self.prediction_button)
        layout.addWidget(self.learning_button)
        layout.addWidget(self.analytics_button)

        # Tạo một widget chứa layout
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def open_prediction_screen(self):
        self.prediction_screen = PredictionScreen()
        self.prediction_screen.show()

    def open_learning_screen(self):
        self.learning_screen = LearningScreen()
        self.learning_screen.show()

    def open_analytics_screen(self):
        self.analytics_screen = AnalyticsScreen()
        self.analytics_screen.show()


class LearningScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Học Ngôn ngữ Ký hiệu")
        layout = QVBoxLayout()

        # Các thành phần cho chức năng học
        self.lesson_button = QPushButton("Xem Bài học")
        self.feedback_button = QPushButton("Gửi Phản hồi")
        
        layout.addWidget(self.lesson_button)
        layout.addWidget(self.feedback_button)

        self.setLayout(layout)

        # Kết nối các nút với các hàm tương ứng
        self.lesson_button.clicked.connect(self.view_lessons)
        self.feedback_button.clicked.connect(self.give_feedback)

    def view_lessons(self):
        # Thêm mã để hiển thị bài học ở đây
        QMessageBox.information(self, "Bài học", "Hiển thị các bài học tại đây.")

    def give_feedback(self):
        # Thêm mã để gửi phản hồi ở đây
        QMessageBox.information(self, "Phản hồi", "Gửi phản hồi tại đây.")


class AnalyticsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phân tích Ký hiệu")
        layout = QVBoxLayout()

        # Các thành phần cho chức năng phân tích
        self.report_button = QPushButton("Tạo Báo cáo")
        self.analysis_button = QPushButton("Phân tích Ký hiệu")

        layout.addWidget(self.report_button)
        layout.addWidget(self.analysis_button)

        self.setLayout(layout)

        # Kết nối các nút với các hàm tương ứng
        self.report_button.clicked.connect(self.generate_report)
        self.analysis_button.clicked.connect(self.analyze_signs)

    def generate_report(self):
        # Thêm mã để tạo báo cáo ở đây
        QMessageBox.information(self, "Báo cáo", "Tạo báo cáo tại đây.")

    def analyze_signs(self):
        # Thêm mã để phân tích ký hiệu ở đây
        QMessageBox.information(self, "Phân tích", "Phân tích ký hiệu tại đây.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

