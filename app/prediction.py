import cv2
import os
import sys 
import numpy as np
import pyttsx3
import time  
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from models.model_loader import load_model
from analytics import DataLogger  
import threading


class PyQtThreadException(Exception):
    """Lỗi xảy ra khi PyQt xử lý không đúng trong thread khác."""
    pass
class WebcamOpenException(Exception):
    pass

class ModelLoadException(Exception):
    pass

class ModelNotLoadedException(Exception):
    pass

class PredictionException(Exception):
    pass

class SignLanguagePredictor:
    def __init__(self, model_path, labels_dict, parent_window):
        self.parent_window = parent_window
        self.model_path = model_path
        self.labels_dict = labels_dict
        self.model = self.load_model()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        self.parent_window = parent_window
        self.bg = None
        self.a_weight = 0.5
        self.logger = DataLogger()  # Giả sử bạn đã có lớp Logger để ghi log
        # Tạo thư mục lưu ảnh nếu chưa tồn tại
        if not os.path.exists("images_captured"):
            os.makedirs("images_captured")

        self.bg = None
        self.a_weight = 0.5
        self.cam = cv2.VideoCapture(0)

        if not self.cam.isOpened():
            raise WebcamOpenException("Không thể mở webcam. Vui lòng kiểm tra kết nối.")

        self.running = True

        # Dictionary chứa các ký hiệu ngôn ngữ (chữ cái và số)
        self.visual_dict = {i: chr(97 + i) for i in range(26)}
        self.visual_dict.update({i + 26: str(i) for i in range(10)})

        # Bộ đếm thời gian cho khung hình
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
        image = image.reshape((1, 64, 64, 1))  # Đảm bảo đúng định dạng đầu vào
        try:
            prediction = self.model.predict(image)
        except Exception as e:
            raise PredictionException(f"Lỗi khi thực hiện dự đoán: {e}")  # Lỗi được bắt
        
        predicted_label = np.argmax(prediction)
        label = self.labels_dict.get(predicted_label, "Unknown")  # Tránh lỗi nếu nhãn không tồn tại
        threading.Thread(target=self.say_sign, args=(label,)).start()

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

                start_time = time.time()  # Bắt đầu đếm thời gian dự đoán
                predicted_sign = self.predict(final_res)  # Dự đoán ký hiệu
                end_time = time.time()  # Kết thúc đếm thời gian

                prediction_time = end_time - start_time  # Tính toán thời gian dự đoán

                # Tạo tên tệp ảnh duy nhất dựa trên thời gian
                image_filename = f"images_captured/hand_{time.strftime('%Y%m%d_%H%M%S')}.jpg"

                # Lưu ảnh tay đã xử lý vào thư mục images_captured/
                cv2.imwrite(image_filename, res)

                # Ghi dữ liệu dự đoán (ký hiệu, độ chính xác, thời gian dự đoán, đường dẫn ảnh)
                self.logger.log(predicted_sign, 1.0, prediction_time, image_filename)

                # Hiển thị ký hiệu dự đoán lên giao diện
                cv2.putText(frame, f'Sign: {predicted_sign}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Cập nhật thông báo UI: Ký hiệu dự đoán và thời gian dự đoán
                self.parent_window.instruction_label.setText(
                    f"Dự đoán: {predicted_sign}. Thời gian: {prediction_time:.2f}s. Chuẩn bị ký hiệu tiếp theo sau 3 giây..."
                )
                self.parent_window.update_frame(frame)

                # Thời gian chờ 3 giây để người dùng chuẩn bị ký hiệu mới
                QTimer.singleShot(3000, lambda: self.parent_window.instruction_label.setText("Đang chờ ký hiệu tiếp theo..."))

                # Tiếp tục dự đoán ký hiệu mới
                self.parent_window.instruction_label.setText("Đang chờ ký hiệu tiếp theo...")
        
        self.parent_window.update_frame(frame)

    def get_frame(self):
        if not self.cam.isOpened():
            raise WebcamOpenException("Không thể mở webcam.")
        
        ret, frame = self.cam.read()
        
        if not ret:
            raise WebcamOpenException("Không thể lấy khung hình từ webcam.")
        
        return frame

    def get_roi(self, frame):
        return frame[100:350, 325:575]

    def preprocess_frame(self, roi):
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(gray, (7, 7), 0)

    def start_prediction(self):
        self.frame_timer.start()

    def stop_prediction(self):
        self.frame_timer.stop()
        self.cleanup()

    def cleanup(self):
        """Giải phóng camera và đóng tất cả cửa sổ."""
        try:
            if self.cam.isOpened():
                self.cam.release()
        finally:
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
        self.prediction_timer = QTimer(self)
        self.prediction_timer.timeout.connect(self.predictor.start_prediction)
        self.prediction_timer.start(30)


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