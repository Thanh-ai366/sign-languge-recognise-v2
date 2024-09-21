import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QWidget, QMessageBox, QStackedWidget)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QThread, pyqtSignal
import pyttsx3
import os
import threading
from dotenv import load_dotenv
from app.prediction import SignLanguagePredictor
from auth.register import Register
from auth.login import UserManager

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

class PredictionThread(QThread):
    update_status = pyqtSignal(str)  # Signal để cập nhật trạng thái GUI

    def run(self):
        model_path = "app/data/saved_models/cnn_model.h5"
        labels_dict = {i: str(i) for i in range(10)}
        labels_dict.update({10 + i: chr(97 + i) for i in range(26)})
        
        predictor = SignLanguagePredictor(model_path, labels_dict)
        predictor.run()  # Giả định rằng hàm này bắt đầu quá trình dự đoán
        self.update_status.emit("Dự đoán hoàn tất")

def set_tts_options(engine):
    speed = 150  # Default speed
    language = 'vi'  # Default language

    engine.setProperty('rate', speed)
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Yuna')  # Vietnamese voice

def start_prediction():
    model_path = "app/data/saved_models/cnn_model.h5"
    labels_dict = {i: str(i) for i in range(10)}
    labels_dict.update({10 + i: chr(97 + i) for i in range(26)})
    predictor = SignLanguagePredictor(model_path, labels_dict)
    predictor.run()

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
        self.username_entry.setStyleSheet("padding: 10px; background-color: #F0F0F0; border-radius: 5px;")
        layout.addWidget(self.username_entry)

        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Mật khẩu")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setStyleSheet("padding: 10px; background-color: #F0F0F0; border-radius: 5px;")
        layout.addWidget(self.password_entry)

        login_button = QPushButton('Đăng nhập', self)
        login_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; font-size: 16px;")
        login_button.clicked.connect(self.login)  # Sửa lỗi ở đây
        layout.addWidget(login_button)

        register_button = QPushButton('Đăng ký', self)
        register_button.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; border-radius: 5px; font-size: 16px;")
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
        self.auth_result_signal.emit(response)  # Emit the result back to the main thread

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
        response = user_manager.register(username, password)
        QMessageBox.information(self, 'Đăng ký', response)
        self.close()

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Phần mềm nhận diện ký hiệu')
        self.setGeometry(100, 100, 800, 600)

        self.toggle_theme_button = QPushButton('Chuyển sang Dark Mode', self)
        self.toggle_theme_button.setGeometry(700, 10, 90, 30)
        self.toggle_theme_button.clicked.connect(self.toggle_theme)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.home_screen = QWidget()
        self.home_layout = QVBoxLayout()

        title = QLabel("Chọn chức năng", self)
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.home_layout.addWidget(title)

        predict_button = QPushButton("Dự đoán ký hiệu", self)
        predict_button.setStyleSheet("padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; font-size: 16px;")
        predict_button.clicked.connect(self.open_predict_screen)
        self.home_layout.addWidget(predict_button)

        feedback_button = QPushButton("Phản hồi", self)
        feedback_button.setStyleSheet("padding: 10px; background-color: #FF9800; color: white; border-radius: 5px; font-size: 16px;")
        feedback_button.clicked.connect(self.open_feedback_screen)
        self.home_layout.addWidget(feedback_button)

        analytics_button = QPushButton("Phân tích dữ liệu", self)
        analytics_button.setStyleSheet("padding: 10px; background-color: #2196F3; color: white; border-radius: 5px; font-size: 16px;")
        analytics_button.clicked.connect(self.open_analytics_screen)
        self.home_layout.addWidget(analytics_button)

        self.home_screen.setLayout(self.home_layout)
        self.central_widget.addWidget(self.home_screen)

        self.predict_screen = PredictScreen()
        self.central_widget.addWidget(self.predict_screen)

        self.feedback_screen = FeedbackScreen()
        self.central_widget.addWidget(self.feedback_screen)

        self.analytics_screen = AnalyticsScreen()
        self.central_widget.addWidget(self.analytics_screen)

    def toggle_theme(self):
        if not self.dark_mode:
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #FFFFFF; }
                QPushButton { background-color: #4CAF50; color: white; }
            """)
            self.toggle_theme_button.setText('Chuyển sang Light Mode')
        else:
            self.setStyleSheet("""
                QWidget { background-color: white; color: black; }
                QPushButton { background-color: #4CAF50; color: white; }
            """)
            self.toggle_theme_button.setText('Chuyển sang Dark Mode')

        self.dark_mode = not self.dark_mode

    def open_predict_screen(self):
        self.central_widget.setCurrentWidget(self.predict_screen)

    def open_feedback_screen(self):
        self.central_widget.setCurrentWidget(self.feedback_screen)

    def open_analytics_screen(self):
        self.central_widget.setCurrentWidget(self.analytics_screen)

class PredictScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.status_label = QLabel("Nhấn nút để bắt đầu dự đoán", self)
        layout.addWidget(self.status_label)

        start_button = QPushButton("Bắt đầu dự đoán", self)
        start_button.clicked.connect(self.start_prediction)  # Kết nối với hàm start_prediction
        layout.addWidget(start_button)

        self.setLayout(layout)
   
    def update_status_label(self, status):
        self.status_label.setText(status)


    def start_prediction(self):
        self.status_label.setText("Đang dự đoán...")
        self.prediction_thread = PredictionThread()  # Khởi tạo luồng dự đoán
        self.prediction_thread.prediction_completed.connect(self.on_prediction_completed)  # Kết nối tín hiệu hoàn thành dự đoán
        self.prediction_thread.start()  # Bắt đầu luồng

        threading.Thread(target=start_prediction).start()
class FeedbackScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.feedback_label = QLabel("Nhập phản hồi của bạn:", self)
        layout.addWidget(self.feedback_label)

        self.feedback_entry = QLineEdit(self)
        layout.addWidget(self.feedback_entry)

        send_button = QPushButton("Gửi phản hồi", self)
        send_button.clicked.connect(self.send_feedback)
        layout.addWidget(send_button)

        self.setLayout(layout)

    def send_feedback(self):
        feedback = self.feedback_entry.text()
        if feedback:
            QMessageBox.information(self, "Phản hồi", "Phản hồi của bạn đã được gửi.")
            self.feedback_entry.clear()
        else:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập phản hồi.")

class AnalyticsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        chart_label = QLabel("Phân tích dữ liệu người dùng:", self)
        layout.addWidget(chart_label)

        self.chart_view = self.create_chart()
        layout.addWidget(self.chart_view)

        self.setLayout(layout)

    def create_chart(self):
        # Dummy data
        set0 = QBarSet("Người dùng mới")
        set1 = QBarSet("Người dùng đăng nhập")

        set0 << 1 << 2 << 3 << 4 << 5 << 6
        set1 << 5 << 0 << 0 << 4 << 0 << 7

        series = QBarSeries()
        series.append(set0)
        series.append(set1)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Phân tích người dùng theo tháng")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        categories = ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        axisY = QValueAxis()
        axisY.setRange(0, 10)
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        return chart_view

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
