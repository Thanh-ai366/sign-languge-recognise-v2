import numpy as np
from models.model_loader import load_model

class FeedbackSystem:
    def __init__(self, model_path, labels_dict):
        self.model = load_model(model_path)
        self.labels_dict = labels_dict

    def evaluate(self, image, correct_label):
        image = image.reshape((1, 64, 64, 1))  # Đảm bảo kích thước đúng
        prediction = self.model.predict(image)
        predicted_label = np.argmax(prediction)
        
        if predicted_label == correct_label:
            return "Chính xác! Ký hiệu của bạn rất tốt."
        else:
            return f"Ký hiệu chưa chính xác. Hãy thử lại và chú ý đến {self.get_improvement_suggestion(correct_label)}."

    def get_improvement_suggestion(self, correct_label):
        return f"cách đặt tay và hướng di chuyển của ký hiệu {self.labels_dict[correct_label]}."

# Sử dụng hệ thống phản hồi
if __name__ == "__main__":
    model_path = "data/saved_models/cnn_model.pkl"
    
    # Ánh xạ nhãn: 0-9 cho số, 10-35 cho ký tự a-z
    labels_dict = {i: str(i) for i in range(10)}
    labels_dict.update({10 + i: chr(97 + i) for i in range(26)})

    feedback_system = FeedbackSystem(model_path, labels_dict)

    # Giả định user_image và correct_label đã được khởi tạo
    # user_image = ...  # Hình ảnh do người dùng cung cấp
    # correct_label = 0  # Ký hiệu đúng tương ứng với hình ảnh

    # response = feedback_system.evaluate(user_image, correct_label)
    # print(response)
