import cv2
import numpy as np
import pyttsx3
from app.utils import preprocess_image
from models.model_loader import load_model
from analytics.data_logger import DataLogger
import threading
import redis

# Kết nối với Redis
cache = redis.Redis(host='localhost', port=6379, db=0)

class SignLanguagePredictor:
    def __init__(self, model_path, labels_dict):
        self.model_path = model_path
        self.labels_dict = labels_dict
        self.model = self.load_model()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.logger = DataLogger("data/logs/sign_usage.csv")

        self.cap = cv2.VideoCapture(0)  # Sử dụng webcam mặc định
        if not self.cap.isOpened():
            raise Exception("Không thể mở webcam. Vui lòng kiểm tra kết nối.")
        self.running = True

    def load_model(self):
        try:
            model = load_model(self.model_path)
            print(f"Mô hình đã được tải thành công từ {self.model_path}")
            return model
        except Exception as e:
            print(f"Lỗi khi tải mô hình: {e}")
            return None

    def preprocess_frame(self, frame):
        # Tiền xử lý khung hình trước khi dự đoán
        resized_frame = cv2.resize(frame, (64, 64))
        normalized_frame = resized_frame / 255.0
        return np.expand_dims(normalized_frame, axis=(0, -1))

    def predict(self, image):
        if self.model is None:
            raise Exception("Mô hình chưa được tải.")
        
        image_key = "image_cache"  # Đặt key cho cache
        cached_prediction = cache.get(image_key)
        if cached_prediction:
            return cached_prediction.decode('utf-8')

        image = image.reshape((1, 64, 64, 1))  # Định dạng cho mô hình
        prediction = self.model.predict(image)
        predicted_label = np.argmax(prediction)
        label = self.labels_dict[predicted_label]

        # Lưu dự đoán vào cache với TTL 1 giờ
        cache.set(image_key, label, ex=3600)  # TTL là 3600 giây (1 giờ)
        return label

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def start_prediction_thread(self):
        previous_sign = None
        prediction_delay = 30
        frame_count = 0
        with open("sign_predictions.txt", "w") as file:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Không thể nhận diện frame từ webcam.")
                    break
                try:
                    normalized_frame = self.preprocess_frame(frame)
                    predicted_sign = self.predict(normalized_frame)

                    self.logger.log(predicted_sign, 1.0, 0.5)
                    cv2.putText(frame, f"Ký hiệu: {predicted_sign}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow("Webcam", frame)
                    frame_count += 1
                    if predicted_sign != previous_sign and frame_count >= prediction_delay:
                        self.speak(predicted_sign)
                        previous_sign = predicted_sign
                        frame_count = 0
                    file.write(f"{predicted_sign}\n")
                except Exception as e:
                    print(f"Lỗi trong quá trình dự đoán: {e}")
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        self.cleanup()

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def run(self):
        if self.model is None:
            print("Mô hình chưa được tải. Dự đoán không thể bắt đầu.")
            return
        prediction_thread = threading.Thread(target=self.start_prediction_thread)
        prediction_thread.start()
