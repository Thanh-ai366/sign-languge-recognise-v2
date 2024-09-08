import cv2
import numpy as np
import pyttsx3
from app.utils import preprocess_image
from models.cnn_model import create_cnn_model
from models.model_loader import load_model
from analytics.data_logger import DataLogger

class SignLanguagePredictor:
    def __init__(self, model_path, labels_dict, input_shape=(64, 64, 1), num_classes=36):
        self.model_path = model_path
        self.labels_dict = labels_dict
        self.model = create_cnn_model(input_shape=input_shape, num_classes=num_classes)
        self.load_model()
        
        # Khởi tạo TTS
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Điều chỉnh tốc độ nói

        # Khởi tạo DataLogger để ghi lại dữ liệu sử dụng
        self.logger = DataLogger("data/logs/sign_usage.csv")

    def load_model(self):
        self.model = load_model(self.model_path)

    def predict(self, image):
        image = image.reshape((1, 64, 64, 1))
        prediction = self.model.predict(image)
        predicted_label = np.argmax(prediction)
        return self.labels_dict[predicted_label]

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Không thể truy cập webcam.")
            return
        
        # Mở tệp văn bản để ghi kết quả dự đoán
        with open("sign_predictions.txt", "w") as file:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Không thể nhận diện frame từ webcam.")
                    break

                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                resized_frame = cv2.resize(gray_frame, (64, 64))
                normalized_frame = resized_frame / 255.0

                # Dự đoán ký hiệu
                predicted_sign = self.predict(normalized_frame)
                
                # Ghi lại dữ liệu sử dụng
                self.logger.log(predicted_sign, 1.0, 0.5)  # Thời gian thực hiện và độ chính xác giả định

                # Hiển thị kết quả dự đoán trên màn hình theo thời gian thực
                cv2.putText(frame, f"Ký hiệu: {predicted_sign}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Webcam", frame)

                # Phát âm lời nói từ ký hiệu
                self.speak(predicted_sign)

                # Tự động lưu kết quả dự đoán vào tệp văn bản
                file.write(f"{predicted_sign}\n")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()
