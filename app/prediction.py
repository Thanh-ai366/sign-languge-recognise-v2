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

        self.cap = cv2.VideoCapture(0) # Sử dụng webcam mặc định
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

    # Tải mô hình đã huấn luyện
model = create_cnn_model()
model.load_weights('saved_models/cnn_model.h5')
 
def preprocess_image(image_path):
    # Đọc và tiền xử lý hình ảnh
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    resized_image = cv2.resize(image, (64, 64))
    normalized_image = resized_image / 255.0
    return np.expand_dims(normalized_image, axis=(0, -1))


    def predict(self, image):
        if self.model is None:
            raise Exception("Mô hình chưa được tải.")
        image = image.reshape((1, 64, 64, 1)) # Định dạng cho mô hình
        prediction = self.model.predict(image)
        predicted_label = np.argmax(prediction)
        return self.labels_dict[predicted_label]

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
