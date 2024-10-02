import sys
import cv2
import numpy as np
import pyttsx3
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
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
    def __init__(self, model_path, labels_dict, parent_window):  # Thêm tham số parent_window
        self.parent_window = parent_window  # Lưu trữ parent_window
        self.model_path = model_path
        self.labels_dict = labels_dict
        self.model = self.load_model()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Tốc độ phát âm mặc định
        self.logger = DataLogger("data/logs/sign_usage.csv")

        self.bg = None
        self.a_weight = 0.5
        self.cam = cv2.VideoCapture(0)  # Sử dụng webcam mặc định

        if not self.cam.isOpened():
            raise WebcamOpenException("Không thể mở webcam. Vui lòng kiểm tra kết nối.")
        
        self.running = True

        self.visual_dict = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 
                            7: '7', 8: '8', 9: '9', 10: 'a', 11: 'b', 12: 'c', 
                            13: 'd', 14: 'e', 15: 'f', 16: 'g', 17: 'h', 18: 'i', 
                            19: 'j', 20: 'k', 21: 'l', 22: 'm', 23: 'n', 24: 'o', 
                            25: 'p', 26: 'q', 27: 'r', 28: 's', 29: 't', 30: 'u', 
                            31: 'v', 32: 'w', 33: 'x', 34: 'y', 35: 'z'}

    def load_model(self):
        try:
            model = load_model(self.model_path)  # Load model từ đường dẫn được truyền vào
            print(f"Mô hình đã được tải thành công từ {self.model_path}")
            return model
        except Exception as e:
            raise ModelLoadException(f"Lỗi khi tải mô hình: {e}")

    def preprocess_frame(self, frame):
        resized_frame = cv2.resize(frame, (100, 100))  # Kích thước phù hợp với mô hình
        normalized_frame = resized_frame / 255.0
        return np.expand_dims(normalized_frame, axis=(0, -1))

    def run_avg(self, image, aweight):
        if self.bg is None:
            self.bg = image.copy().astype("float")
            return
        cv2.accumulateWeighted(image, self.bg, aweight)

    def extract_hand(self, image, threshold=25):
        diff = cv2.absdiff(self.bg.astype("uint8"), image)
        thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]
        cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) == 0:
            return
        else:
            max_cont = max(cnts, key=cv2.contourArea)
            return (thresh, max_cont)

    def say_sign(self, sign):
        self.engine.say(sign)
        self.engine.runAndWait()

    def predict(self, image):
        image_hash = str(hash(image.tobytes()))
        cached_prediction = cache.get(image_hash)
        
        if cached_prediction:
            return cached_prediction.decode('utf-8')

        image = image.reshape((1, 100, 100, 1))  # Định dạng cho mô hình
        try:
            prediction = self.model.predict(image)
        except Exception as e:
            raise PredictionException(f"Lỗi khi thực hiện dự đoán: {e}")

        predicted_label = np.argmax(prediction)
        label = self.labels_dict[predicted_label]

        # Lưu dự đoán vào cache với TTL 1 giờ
        cache.set(image_hash, label, ex=3600)  # TTL là 3600 giây (1 giờ)
        
        # Phát âm ký hiệu ngay sau khi nhận diện thành công
        threading.Thread(target=self.say_sign, args=(label,)).start()

        return label

    def start_prediction(self):
        count = 0
        result_list = []
        prev_sign = None

        while self.cam.isOpened():
            frame = self.get_frame()
            if frame is None:
                break

            # Gọi hàm update_frame từ đối tượng PredictionWindow
            # Thay thế dòng cv2.imshow("Video Feed", frame) bằng:
            self.parent_window.update_frame(frame)

            roi = self.get_roi(frame)
            gray = self.preprocess_image(roi)

            if count < 30:
                self.run_avg(gray, self.a_weight)
            else:
                self.process_hand(gray, roi, frame, count, result_list, prev_sign)

            count += 1

            if self.check_exit_key():
                break

        self.cleanup()

    def get_frame(self):
        _, frame = self.cam.read()
        if frame is None:
            raise WebcamOpenException("Không thể lấy khung hình từ webcam.")
        return frame

    def get_roi(self, frame):
        return frame[100:350, 325:575]  # Khu vực quan sát

    def preprocess_image(self, roi):
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(gray, (7, 7), 0)

    def process_hand(self, gray, roi, frame, count, result_list, prev_sign):
        hand = self.extract_hand(gray)
        if hand is not None:
            thresh, _ = hand
            res = cv2.bitwise_and(roi, roi, mask=thresh)
            res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

            final_res = self.preprocess_frame(res)
            predicted_sign = self.predict(final_res)

            self.update_results(count, predicted_sign, result_list, prev_sign)
            self.display_prediction(frame, predicted_sign)

    def update_results(self, count, predicted_sign, result_list, prev_sign):
        if count > 10:
            result_list.append(predicted_sign)
            if count % 50 == 0 and result_list:
                final_sign = max(set(result_list), key=result_list.count)
                if prev_sign != final_sign:
                    return final_sign
        return prev_sign

    def display_prediction(self, frame, predicted_sign):
        cv2.putText(frame, 'Sign: ' + predicted_sign, (10, 200), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255))

    def check_exit_key(self):
        return cv2.waitKey(1) & 0xFF == 27  # Esc key to exit

    def cleanup(self):
        self.cam.release()
        cv2.destroyAllWindows()

# Giao diện chính
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ngôn ngữ ký hiệu - Prediction")
        
        # Khởi tạo bộ dự đoán với mô hình mới
        self.predictor = SignLanguagePredictor("C:/Users/ASUS/Downloads/sign-languge-recognise-v2/app/data/saved_models/cnn_model_best.keras", 
                                                labels_dict=self.get_labels_dict(), 
                                                parent_window=self)  # Chuyển self vào

        # Nút để mở cửa sổ dự đoán
        self.start_prediction_button = QPushButton("Bắt đầu dự đoán")
        self.start_prediction_button.clicked.connect(self.open_prediction_window)

        # Tạo layout chính
        layout = QVBoxLayout()
        layout.addWidget(self.start_prediction_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_prediction_window(self):
        self.prediction_window = PredictionWindow(self)  # Truyền self vào PredictionWindow
        self.prediction_window.show()
    
    def get_labels_dict(self):
        return {
            0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6',
            7: '7', 8: '8', 9: '9', 10: 'a', 11: 'b', 12: 'c',
            13: 'd', 14: 'e', 15: 'f', 16: 'g', 17: 'h', 18: 'i',
            19: 'j', 20: 'k', 21: 'l', 22: 'm', 23: 'n', 24: 'o',
            25: 'p', 26: 'q', 27: 'r', 28: 's', 29: 't', 30: 'u',
            31: 'v', 32: 'w', 33: 'x', 34: 'y', 35: 'z'
        }

# Giao diện video từ camera và thực hiện dự đoán
class PredictionWindow(QDialog):
    def __init__(self, parent_window):  # Thêm tham số parent_window
        super().__init__()
        self.parent_window = parent_window  # Lưu trữ parent_window
        self.setWindowTitle("Dự đoán ngôn ngữ ký hiệu")

        # Khởi tạo bộ dự đoán với mô hình mới
        self.predictor = SignLanguagePredictor("C:/Users/ASUS/Downloads/sign-languge-recognise-v2/app/data/saved_models/cnn_model_best.keras", 
                                                labels_dict=self.get_labels_dict(), 
                                                parent_window=self)  # Truyền self vào

        # Nhãn để hiển thị dự đoán
        self.result_label = QLabel("Dự đoán: ")
        self.result_label.setStyleSheet("font-size: 20px; color: red;")

        # Nhãn để hiển thị video
        self.video_label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.result_label)

        # Nút kết thúc dự đoán
        self.stop_button = QPushButton("Dừng dự đoán")
        self.stop_button.clicked.connect(self.stop_prediction)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        # Khởi chạy dự đoán trong luồng riêng
        self.prediction_thread = threading.Thread(target=self.predictor.start_prediction)
        self.prediction_thread.start()

    def update_frame(self, frame):
        # Chuyển đổi khung hình sang QImage và hiển thị trên QLabel
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def stop_prediction(self):
        self.predictor.running = False
        self.close()

    def get_labels_dict(self):
        return {
            0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6',
            7: '7', 8: '8', 9: '9', 10: 'a', 11: 'b', 12: 'c',
            13: 'd', 14: 'e', 15: 'f', 16: 'g', 17: 'h', 18: 'i',
            19: 'j', 20: 'k', 21: 'l', 22: 'm', 23: 'n', 24: 'o',
            25: 'p', 26: 'q', 27: 'r', 28: 's', 29: 't', 30: 'u',
            31: 'v', 32: 'w', 33: 'x', 34: 'y', 35: 'z'
        }

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
