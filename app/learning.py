# learning.py
import json
import numpy as np
from datetime import datetime
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf

# ----------------------------------------------------
# Khai báo lớp Feedback
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
            feedback_entry['suggestion'] = "Ký hiệu sai. Bạn nên thực hiện động tác với độ chính xác cao hơn ở ngón tay và góc nhìn."

        self.feedback_data[timestamp] = feedback_entry
        self.save_feedback_data()

    def get_feedback_history(self):
        history = [
            f"Thời gian: {entry['timestamp']}, Thực tế: {entry['actual']}, Dự đoán: {entry['predicted']}, Đúng/Sai: {'Đúng' if entry['correct'] else 'Sai'}, Gợi ý: {entry['suggestion']}"
            for entry in self.feedback_data.values()
        ]
        return history


# ----------------------------------------------------
# Khai báo lớp Lesson
class Lesson:
    DEFAULT_LEVEL = "Cơ bản"

    def __init__(self, sign, instruction, level=DEFAULT_LEVEL, image_path=None):
        self.sign = sign
        self.instruction = instruction
        self.level = level
        self.image_path = image_path

    def get_instruction(self):
        return self.instruction

    def get_sign(self):
        return self.sign

    def get_image_path(self):
        return self.image_path
    
    def get_level(self):
        return self.level


class LessonManager:
    def __init__(self, lessons_file="learning/lessons_data.json"):
        self.lessons_file = lessons_file
        self.lessons = self.load_lessons()

    def load_lessons(self):
        try:
            with open(self.lessons_file, 'r') as file:
                lessons_data = json.load(file)
                return [Lesson(sign, instruction, level) for level, signs in lessons_data.items() for sign, instruction in signs.items()]
        except FileNotFoundError:
            return []

    def save_lessons(self):
        lessons_data = {}
        for lesson in self.lessons:
            if lesson.get_level() not in lessons_data:
                lessons_data[lesson.get_level()] = {}
            lessons_data[lesson.get_level()][lesson.get_sign()] = lesson.get_instruction()
        
        try:
            with open(self.lessons_file, 'w') as file:
                json.dump(lessons_data, file)
            print("Dữ liệu bài học đã được lưu.")
        except Exception as e:
            print(f"Lỗi khi lưu bài học: {e}")

    def add_lesson(self, sign, instruction, level="Cơ bản", image_path=None):
        lesson = Lesson(sign, instruction, level, image_path)
        self.lessons.append(lesson)
        self.save_lessons()

    def get_lessons_by_level(self, level):
        return [lesson for lesson in self.lessons if lesson.get_level() == level]

    def get_lessons(self):
        return self.lessons


# ----------------------------------------------------
# Khai báo lớp ProgressTracker
class ProgressTracker:
    def __init__(self, username, progress_file="learning/progress_data.json"):
        self.username = username
        self.progress_file = progress_file
        self.progress_data = self.load_progress_data()

    def load_progress_data(self):
        try:
            with open(self.progress_file, 'r') as file:
                all_progress = json.load(file)
                return all_progress.get(self.username, {})
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu tiến độ: {e}")
            return {}

    def save_progress_data(self):
        try:
            with open(self.progress_file, 'r') as file:
                all_progress = json.load(file)
        except FileNotFoundError:
            all_progress = {}
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu tiến độ: {e}")
            all_progress = {}

        all_progress[self.username] = self.progress_data

        try:
            with open(self.progress_file, 'w') as file:
                json.dump(all_progress, file)
            print("Dữ liệu tiến độ đã được lưu.")
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu tiến độ: {e}")

    def update_progress(self, lesson, accuracy):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        progress_entry = {
            'lesson': lesson,
            'accuracy': accuracy,
            'timestamp': timestamp
        }

        self.progress_data[timestamp] = progress_entry
        self.save_progress_data()

    def get_progress_report(self):
        report = [
            f"Buổi học: {entry['lesson']}, Độ chính xác: {entry['accuracy']}, Thời gian: {entry['timestamp']}"
            for entry in self.progress_data.values()
        ]
        return report


# ----------------------------------------------------
# Khai báo lớp ImageAnalyzer
class ImageAnalyzer:
    def __init__(self, model_path):  # Thêm mô hình CNN vào đây
        # Tải mô hình CNN từ tệp
        self.model = tf.keras.models.load_model(model_path)
        self.label_map = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}  # Bản đồ nhãn mẫu (cập nhật theo nhãn của bạn)

    def capture_image(self):
        """Chụp ảnh từ camera."""
        cap = cv2.VideoCapture(0)  # Mở camera
        ret, frame = cap.read()  # Đọc khung hình
        cap.release()  # Đóng camera
        if ret:
            return frame
        else:
            print("Không thể chụp ảnh.")
            return None

    def preprocess_image(self, image):
        """Tiền xử lý hình ảnh trước khi phân tích."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (64, 64))  # Thay đổi kích thước theo mô hình
        normalized = resized / 255.0  # Chuẩn hóa giá trị pixel
        return normalized.reshape(1, 64, 64, 1)  # Định dạng cho mô hình CNN

    def predict(self, image):
        """Dự đoán nhãn ký hiệu từ hình ảnh."""
        processed_image = self.preprocess_image(image)
        prediction = self.model.predict(processed_image)  # Dự đoán bằng mô hình CNN
        predicted_label_index = np.argmax(prediction)  # Lấy nhãn với xác suất cao nhất
        predicted_label = self.label_map.get(predicted_label_index, "Unknown")  # Tra cứu nhãn từ bản đồ
        return predicted_label

    def evaluate_prediction(self, actual_label, predicted_label):
        """Đánh giá độ chính xác của dự đoán."""
        return actual_label == predicted_label  # So sánh nhãn thực tế và dự đoán

    def display_instruction(self, image_path):
        """Hiển thị hình ảnh hướng dẫn."""
        img = plt.imread(image_path)
        plt.imshow(img)
        plt.axis('off')  # Ẩn trục
        plt.show()


# ----------------------------------------------------
# Hàm khởi động quá trình học
def start_learning(username):
    lesson_manager = LessonManager()
    feedback = Feedback(username)
    image_analyzer = ImageAnalyzer("model.h5")  # Thêm mô hình CNN vào đây

    # Thêm 35 bài học ví dụ
    lessons_data = [
        ("A", "Giơ tay lên và duỗi các ngón tay ra.", "Cơ bản", "images/A.png"),
        ("B", "Đặt ngón cái và ngón trỏ lại với nhau.", "Cơ bản", "images/B.png"),
        ("C", "Gập ngón trỏ lại.", "Cơ bản", "images/C.png"),
        ("D", "Giơ tay trái ra.", "Cơ bản", "images/D.png"),
        ("E", "Gập ngón giữa lại.", "Cơ bản", "images/E.png"),
        ("F", "Giơ cả hai tay lên.", "Cơ bản", "images/F.png"),
        ("G", "Đặt ngón cái lên trán.", "Cơ bản", "images/G.png"),
        ("H", "Gập ngón út lại.", "Cơ bản", "images/H.png"),
        ("I", "Giơ một tay ra và giữ thẳng.", "Cơ bản", "images/I.png"),
        ("J", "Đặt cả hai tay xuống.", "Cơ bản", "images/J.png"),
        ("K", "Vắt ngón tay lại.", "Cơ bản", "images/K.png"),
        ("L", "Giơ ngón tay giữa ra.", "Cơ bản", "images/L.png"),
        ("M", "Đặt tay lên đầu.", "Cơ bản", "images/M.png"),
        ("N", "Đặt tay lên ngực.", "Cơ bản", "images/N.png"),
        ("O", "Giơ tay lên và tạo hình tròn.", "Cơ bản", "images/O.png"),
        ("P", "Gập hai tay lại với nhau.", "Cơ bản", "images/P.png"),
        ("Q", "Giơ tay ra và xoay tròn.", "Cơ bản", "images/Q.png"),
        ("R", "Đặt tay lên bụng.", "Cơ bản", "images/R.png"),
        ("S", "Tạo hình chữ S bằng tay.", "Cơ bản", "images/S.png"),
        ("T", "Gập cả hai tay lại.", "Cơ bản", "images/T.png"),
        ("U", "Đưa tay lên cao.", "Cơ bản", "images/U.png"),
        ("V", "Giơ tay tạo hình chữ V.", "Cơ bản", "images/V.png"),
        ("W", "Đưa tay ra trước mặt.", "Cơ bản", "images/W.png"),
        ("X", "Gập ngón tay cái và trỏ lại.", "Cơ bản", "images/X.png"),
        ("Y", "Giơ ngón tay cái và ngón út ra.", "Cơ bản", "images/Y.png"),
        ("Z", "Tạo hình chữ Z bằng tay.", "Cơ bản", "images/Z.png"),
        # Thêm 10 bài học khác (hoặc thêm tùy ý)
        # ...
    ]

    for lesson in lessons_data:
        lesson_manager.add_lesson(*lesson)  # Thêm bài học vào quản lý bài học

    lessons = lesson_manager.get_lessons()

    # Hiển thị danh sách bài học cho người dùng
    for lesson in lessons:
        print(f"Cấp độ: {lesson.get_level()} - Ký hiệu: {lesson.get_sign()} - Hướng dẫn: {lesson.get_instruction()}")
    
    # Giả sử người dùng chọn một bài học
    selected_lesson = lessons[0]  # Bạn có thể thay đổi cách chọn bài học

    image_analyzer.display_instruction(selected_lesson.get_image_path())

    img = image_analyzer.capture_image()
    if img is not None:
        predicted_label = image_analyzer.predict(img)

        accuracy = image_analyzer.evaluate_prediction(selected_lesson.get_sign(), predicted_label)

        feedback.give_feedback(selected_lesson.get_sign(), predicted_label)

        print(f"Độ chính xác: {accuracy}")

if __name__ == "__main__":
    start_learning("user123")  # Thay "user123" bằng tên người dùng thực tế
