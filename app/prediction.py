import sys
import cv2
import numpy as np
import pyttsx3
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer,Qt
from models.model_loader import load_model
from analytics import DataLogger
import threading
import redis

# Kết nối với Redis
cache = redis.Redis(host='localhost', port=6379, db=0)

# Định nghĩa các lớp ngoại lệ tùy chỉnh
class WebcamOpenException(Exception):
    pass

class ModelLoadException(Exception):
    pass

class ModelNotLoadedException(Exception):
    pass

class PredictionException(Exception):
    pass

# Lớp SignLanguagePredictor chứa toàn bộ logic dự đoán
class SignLanguagePredictor:
    def __init__(self, model_path, labels_dict, parent_window):
        self.parent_window = parent_window
        self.model_path = model_path
        self.labels_dict = labels_dict
        self.model = self.load_model()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.logger = DataLogger("data/logs/sign_usage.csv")
        
        self.bg = None
        self.a_weight = 0.5
        self.cam = cv2.VideoCapture(0)

        if not self.cam.isOpened():
            raise WebcamOpenException("Không thể mở webcam. Vui lòng kiểm tra kết nối.")

        self.running = True

        self.visual_dict = {i: chr(97 + i) for i in range(26)}
        self.visual_dict.update({i + 26: str(i) for i in range(10)})

        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.process_next_frame)
        self.frame_timer.start(30)

    def load_model(self):
        try:
            model = load_model(self.model_path)
            print(f"Mô hình đã được tải thành công từ {self.model_path}")
            return model
        except Exception as e:
            raise ModelLoadException(f"Lỗi khi tải mô hình: {e}")

    def preprocess_frame(self, frame):
        resized_frame = cv2.resize(frame, (64, 64))
        normalized_frame = resized_frame / 255.0
        flattened_frame = normalized_frame.flatten()
        return np.expand_dims(flattened_frame, axis=0)

    def run_avg(self, image, aweight):
        if self.bg is None:
            self.bg = image.copy().astype("float")
        else:
            cv2.accumulateWeighted(image, self.bg, aweight)

    def extract_hand(self, image, threshold=25):
        diff = cv2.absdiff(self.bg.astype("uint8"), image)
        thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]
        cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) == 0:
            return None
        else:
            max_cont = max(cnts, key=cv2.contourArea)
            return thresh, max_cont

    def say_sign(self, sign):
        self.engine.say(sign)
        self.engine.runAndWait()

    def predict(self, image):
        image = image.reshape((1, 64, 64, 1))
        try:
            prediction = self.model.predict(image)
        except Exception as e:
            raise PredictionException(f"Lỗi khi thực hiện dự đoán: {e}")

        predicted_label = np.argmax(prediction)
        label = self.labels_dict[predicted_label]

        threading.Thread(target=self.say_sign, args=(label,)).start()

        return label

    def process_next_frame(self):
        frame = self.get_frame()
        if frame is None:
            return

        cv2.rectangle(frame, (325, 100), (575, 350), (0, 255, 0), 2)

        roi = self.get_roi(frame)
        gray = self.preprocess_image(roi)

        if self.bg is None:
            self.run_avg(gray, self.a_weight)
        else:
            hand = self.extract_hand(gray)
            if hand is not None:
                thresh, _ = hand
                res = cv2.bitwise_and(roi, roi, mask=thresh)
                res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

                final_res = self.preprocess_frame(res)
                predicted_sign = self.predict(final_res)

                cv2.putText(frame, f'Sign: {predicted_sign}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        self.parent_window.update_frame(frame)

    def get_frame(self):
        ret, frame = self.cam.read()
        if not ret:
            raise WebcamOpenException("Không thể lấy khung hình từ webcam.")
        return frame

    def get_roi(self, frame):
        return frame[100:350, 325:575]

    def preprocess_image(self, roi):
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(gray, (7, 7), 0)

    def start_prediction(self):
        self.frame_timer.start()

    def stop_prediction(self):
        self.frame_timer.stop()
        self.cleanup()

    def cleanup(self):
        self.cam.release()
        cv2.destroyAllWindows()

# Giao diện chính
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ngôn ngữ ký hiệu - Prediction")

        # Create layout first
        layout = QVBoxLayout()

        # Create and add video label
        self.video_label = QLabel(self)
        layout.addWidget(self.video_label)

        # Khởi tạo bộ dự đoán với mô hình
        self.predictor = SignLanguagePredictor(
            model_path="C:/Users/ASUS/Downloads/sign-languge-recognise-v2/app/data/saved_models/cnn_model_best.keras", 
            labels_dict=self.get_labels_dict(), 
            parent_window=self
        )

        # Nút để bắt đầu dự đoán
        self.start_prediction_button = QPushButton("Bắt đầu dự đoán")
        self.start_prediction_button.clicked.connect(self.open_prediction_window)
        layout.addWidget(self.start_prediction_button)

        # Set the layout to a container widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def update_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled_pixmap = QPixmap.fromImage(q_img).scaled(640, 480, Qt.KeepAspectRatio)
        self.video_label.setPixmap(scaled_pixmap)

    def open_prediction_window(self):
        self.prediction_window = PredictionWindow(self)
        self.prediction_window.show()

    def get_labels_dict(self):
        # Trả về labels_dict cho bộ dự đoán
        return {i: chr(97 + i) for i in range(26)} | {i + 26: str(i) for i in range(10)}

# Giao diện PredictionWindow hiển thị video từ camera và thực hiện dự đoán
class PredictionWindow(QDialog):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window  # Lưu trữ parent_window
        self.setWindowTitle("Dự đoán ngôn ngữ ký hiệu")

        # Khởi tạo bộ dự đoán
        self.predictor = SignLanguagePredictor(
            model_path="C:/Users/ASUS/Downloads/sign-languge-recognise-v2/app/data/saved_models/cnn_model_best.keras", 
            labels_dict=self.get_labels_dict(), 
            parent_window=self
        )

        # Nhãn hiển thị kết quả dự đoán
        self.result_label = QLabel("Dự đoán: ")
        self.result_label.setStyleSheet("font-size: 20px; color: red;")

        # Nhãn hướng dẫn người dùng
        self.instruction_label = QLabel("Vui lòng đặt tay vào vùng hình chữ nhật.")
        self.instruction_label.setStyleSheet("font-size: 16px; color: blue;")

        # Nhãn hiển thị video
        self.video_label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.instruction_label)  # Hiển thị hướng dẫn
        layout.addWidget(self.result_label)

        # Nút để dừng dự đoán
        self.stop_button = QPushButton("Dừng dự đoán")
        self.stop_button.clicked.connect(self.stop_prediction)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        # Chạy dự đoán trong luồng riêng
        self.prediction_thread = threading.Thread(target=self.predictor.start_prediction)
        self.prediction_thread.start()


    def update_frame(self, frame):
        # Cập nhật khung hình video lên giao diện
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        cv2.rectangle(frame, (325, 100), (575, 350), (0, 255, 0), 2)

        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def stop_prediction(self):
        self.predictor.running = False
        self.predictor.cleanup()  # Giải phóng tài nguyên
        self.close()


    def get_labels_dict(self):
        # Trả về labels_dict
        return {i: chr(97 + i) for i in range(26)} | {i + 26: str(i) for i in range(10)}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
