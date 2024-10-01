import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QStackedWidget, QWidget, QLabel, QLineEdit, QFormLayout, QDialog, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import cv2
import numpy as np
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))

from models.model_loader import load_model
from analytics import DataLogger

sys.path.append(r'C:/Users/ASUS/Downloads/sign-languge-recognise v2/app/learning.py')

from learning import Feedback, LessonManager, ProgressTracker

sys.path.append(r'C:/Users/ASUS/Downloads/sign-languge-recognise v2/app/analytics.py')

from analytics import SignAnalysis, ReportGenerator

sys.path.append(r'C:/Users/ASUS/Downloads/sign-languge-recognise v2/app/prediction.py')

from prediction import SignLanguagePredictor


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


# Lớp PredictionThread để xử lý dự đoán trong luồng riêng biệt
class PredictionThread(QThread):
    prediction_signal = pyqtSignal(str)  # Tín hiệu gửi kết quả dự đoán

    def __init__(self, predictor, parent=None):
        super().__init__(parent)
        self.predictor = predictor  # Đối tượng SignLanguagePredictor để thực hiện dự đoán
        self.running = True  # Cờ để kiểm soát quá trình chạy

    def run(self):
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


# Lớp LoginWindow cho giao diện đăng nhập
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Đăng nhập')
        self.setGeometry(400, 150, 300, 150)

        self.username_label = QLabel('Tên người dùng')
        self.password_label = QLabel('Mật khẩu')

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('Đăng nhập')
        self.register_button = QPushButton('Đăng ký')

        form_layout = QFormLayout()
        form_layout.addRow(self.username_label, self.username_input)
        form_layout.addRow(self.password_label, self.password_input)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        # Sự kiện nhấn nút
        self.login_button.clicked.connect(self.check_login)
        self.register_button.clicked.connect(self.open_register)

    def check_login(self):
        # Logic kiểm tra đăng nhập (giả lập)
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "user" and password == "password":
            self.accept()
        else:
            QMessageBox.warning(self, 'Lỗi đăng nhập', 'Tên người dùng hoặc mật khẩu không đúng')

    def open_register(self):
        register_window = RegisterWindow(self)
        register_window.exec_()

# Lớp RegisterWindow cho giao diện đăng ký
class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Đăng ký')
        self.setGeometry(400, 150, 300, 150)

        self.username_label = QLabel('Tên người dùng')
        self.password_label = QLabel('Mật khẩu')
        self.confirm_password_label = QLabel('Xác nhận mật khẩu')

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.register_button = QPushButton('Đăng ký')

        form_layout = QFormLayout()
        form_layout.addRow(self.username_label, self.username_input)
        form_layout.addRow(self.password_label, self.password_input)
        form_layout.addRow(self.confirm_password_label, self.confirm_password_input)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        # Sự kiện nhấn nút
        self.register_button.clicked.connect(self.register)

    def register(self):
        # Lấy giá trị từ các trường nhập liệu
        username = self.username_input.text()  # Sử dụng username
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if password != confirm_password:
            QMessageBox.warning(self, 'Lỗi đăng ký', 'Mật khẩu không trùng khớp')
        else:
            # Xử lý đăng ký với username (ví dụ: lưu vào cơ sở dữ liệu)
            print(f"Đăng ký thành công cho tài khoản: {username}")  # Hiển thị thông báo với username
            QMessageBox.information(self, 'Thành công', 'Đăng ký thành công!')
            self.accept()


# Lớp PredictionScreen để dự đoán ký hiệu
class PredictionScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dự đoán ngôn ngữ ký hiệu")

        # Tạo bộ dự đoán
        self.predictor = SignLanguagePredictor("model.h5", labels_dict=self.get_labels_dict())

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
                9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 
                17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z'}


# Lớp LearningScreen để học ngôn ngữ ký hiệu
class LearningScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Học ngôn ngữ ký hiệu")

        # Khởi tạo lớp học
        self.feedback = Feedback("user123")
        self.lesson_manager = LessonManager()

        # Hiển thị các bài học
        self.lesson_label = QLabel("Chọn bài học để bắt đầu")
        self.lesson_label.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton("Bắt đầu học")
        self.progress_button = QPushButton("Xem tiến độ")

        layout = QVBoxLayout()
        layout.addWidget(self.lesson_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_button)

        self.setLayout(layout)

        # Sự kiện nhấn nút
        self.start_button.clicked.connect(self.start_lesson)
        self.progress_button.clicked.connect(self.view_progress)

    def start_lesson(self):
        lessons = self.lesson_manager.get_lessons()
        if lessons:
            selected_lesson = lessons[0]  # Giả sử chọn bài học đầu tiên
            self.lesson_label.setText(f"Bắt đầu học ký hiệu: {selected_lesson.get_sign()}")

    def view_progress(self):
        progress_tracker = ProgressTracker("user123")
        progress_report = progress_tracker.get_progress_report()
        QMessageBox.information(self, "Tiến độ học tập", "\n".join(progress_report))


# Lớp AnalyticsScreen để phân tích dữ liệu
class AnalyticsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phân tích dữ liệu")

        # Khởi tạo lớp phân tích
        self.analysis = SignAnalysis("data/logs/sign_usage.csv")
        self.report_generator = ReportGenerator("Báo cáo phân tích")

        self.analysis_label = QLabel("Phân tích dữ liệu và tạo báo cáo")
        self.analysis_label.setAlignment(Qt.AlignCenter)

        self.generate_report_button = QPushButton("Tạo báo cáo")
        self.view_analysis_button = QPushButton("Xem phân tích")

        layout = QVBoxLayout()
        layout.addWidget(self.analysis_label)
        layout.addWidget(self.generate_report_button)
        layout.addWidget(self.view_analysis_button)

        self.setLayout(layout)

        # Sự kiện nhấn nút
        self.generate_report_button.clicked.connect(self.generate_report)
        self.view_analysis_button.clicked.connect(self.view_analysis)

    def generate_report(self):
        self.analysis.generate_report()
        QMessageBox.information(self, "Báo cáo", "Báo cáo đã được tạo thành công!")

    def view_analysis(self):
        self.analysis.plot_accuracy()


# Lớp MainApp để quản lý toàn bộ giao diện chính
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng dụng Ngôn ngữ Ký hiệu")

        self.stacked_widget = QStackedWidget()

        # Tạo các màn hình khác nhau
        self.login_screen = LoginWindow()
        self.prediction_screen = PredictionScreen()
        self.learning_screen = LearningScreen()
        self.analytics_screen = AnalyticsScreen()

        # Thêm vào stacked widget
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.prediction_screen)
        self.stacked_widget.addWidget(self.learning_screen)
        self.stacked_widget.addWidget(self.analytics_screen)

        self.setCentralWidget(self.stacked_widget)

        # Khi đăng nhập thành công, chuyển sang giao diện chính
        self.login_screen.login_button.clicked.connect(self.show_main_menu)

    def show_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.prediction_screen)


# Chạy chương trình
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
