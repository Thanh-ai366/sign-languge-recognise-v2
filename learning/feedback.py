import json
import numpy as np
from datetime import datetime

class Feedback:
    def __init__(self, username, feedback_file="learning/user_feedback.json"):
        self.username = username
        self.feedback_file = feedback_file
        self.feedback_data = self.load_feedback_data()

    def load_feedback_data(self):
        try:
            with open(self.feedback_file, 'r') as file:
                all_feedback = json.load(file)
                return all_feedback.get(self.username, {})
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Lỗi khi tải phản hồi người dùng: {e}")
            return {}

    def save_feedback_data(self):
        try:
            with open(self.feedback_file, 'r') as file:
                all_feedback = json.load(file)
        except FileNotFoundError:
            all_feedback = {}
        except Exception as e:
            print(f"Lỗi khi tải phản hồi người dùng: {e}")
            all_feedback = {}

        all_feedback[self.username] = self.feedback_data

        try:
            with open(self.feedback_file, 'w') as file:
                json.dump(all_feedback, file)
            print("Phản hồi của người dùng đã được lưu.")
        except Exception as e:
            print(f"Lỗi khi lưu phản hồi: {e}")

    def give_feedback(self, actual_label, predicted_label):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feedback_entry = {
            'timestamp': timestamp,
            'actual': actual_label,
            'predicted': predicted_label,
            'correct': actual_label == predicted_label
        }

        if actual_label == predicted_label:
            feedback_entry['suggestion'] = "Ký hiệu đúng. Tiếp tục luyện tập để duy trì phong độ!"
        else:
            feedback_entry['suggestion'] = f"Ký hiệu sai. Bạn nên thực hiện động tác với độ chính xác cao hơn ở ngón tay và góc nhìn."

        self.feedback_data[timestamp] = feedback_entry
        self.save_feedback_data()

    def get_feedback_history(self):
        history = [
            f"Thời gian: {entry['timestamp']}, Thực tế: {entry['actual']}, Dự đoán: {entry['predicted']}, Đúng/Sai: {'Đúng' if entry['correct'] else 'Sai'}, Gợi ý: {entry['suggestion']}"
            for entry in self.feedback_data.values()
        ]
        return history
