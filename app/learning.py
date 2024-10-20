#learning.py 
import json
import os
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from datetime import datetime
import cv2
from jwt import ExpiredSignatureError, InvalidTokenError
import matplotlib.pyplot as plt
import tensorflow as tf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import jwt

# Đường dẫn đến thư mục dữ liệu của người dùng
USER_DATA_DIR = "data/user_learning_data"
LEARNING_DATA_DIR = "learning"

# Tự động tạo thư mục nếu chưa tồn tại
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(LEARNING_DATA_DIR, exist_ok=True)

# Tạo engine SQLAlchemy và session
engine = create_engine('sqlite:///data/users.db')
Session = sessionmaker(bind=engine)
session = Session()

# ----------------------------------------------------

def get_user_data_path(token):
    try:
        decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
        username = decoded_token['username']
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException("Token hết hạn. Vui lòng đăng nhập lại.")
    except jwt.InvalidTokenError:
        raise InvalidTokenException("Token không hợp lệ. Vui lòng đăng nhập lại.")

    user_data_path = os.path.join(USER_DATA_DIR, username)
    if not os.path.exists(user_data_path):
        os.makedirs(user_data_path)
    
    return user_data_path

# ----------------------------------------------------

def start_learning(token):
    user_data_path = get_user_data_path(token)
    if user_data_path:
        # Bắt đầu quá trình học với dữ liệu riêng của người dùng
        print(f"Bắt đầu học cho người dùng tại: {user_data_path}")

# ----------------------------------------------------
# Lớp LearningAPP
class LearningApp(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.lesson_manager = LessonManager()  # Quản lý bài học
        self.feedback = Feedback(self.username)  # Quản lý phản hồi
        self.image_analyzer = ImageAnalyzer("C:/Users/ASUS/Downloads/sign-languge-recognise-v2/app/data/saved_models/cnn_model_best.keras")  # Phân tích hình ảnh
        self.progress_tracker = ProgressTracker(self.username)  # Theo dõi tiến trình học tập

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Học ngôn ngữ ký hiệu")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Danh sách bài học
        self.lesson_list = QListWidget()
        for lesson in self.lesson_manager.get_lessons():
            self.lesson_list.addItem(f"{lesson.get_sign()} - {lesson.get_level()}")
        self.lesson_list.clicked.connect(self.display_lesson)

        # Nhãn hiển thị hình ảnh và hướng dẫn
        self.image_label = QLabel("Hình ảnh ký hiệu sẽ được hiển thị ở đây")
        self.image_label.setFixedSize(300, 300)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.instruction_label = QLabel("Hướng dẫn ký hiệu sẽ được hiển thị ở đây")
        self.instruction_label.setWordWrap(True)

        # Nút để chụp ảnh và thực hiện dự đoán
        self.capture_button = QPushButton("Chụp ảnh và dự đoán")
        self.capture_button.clicked.connect(self.capture_image_and_predict)

        # Nút để hiển thị tiến trình học tập
        self.progress_button = QPushButton("Xem tiến trình học tập")
        self.progress_button.clicked.connect(self.display_progress)

        # Thêm các widget vào layout
        layout.addWidget(self.lesson_list)
        layout.addWidget(self.image_label)
        layout.addWidget(self.instruction_label)
        layout.addWidget(self.capture_button)
        layout.addWidget(self.progress_button)

        self.setLayout(layout)

    def display_lesson(self):
        """Hiển thị bài học khi người dùng chọn một bài học"""
        selected_item = self.lesson_list.currentItem().text().split(" - ")[0]
        lesson = next(l for l in self.lesson_manager.get_lessons() if l.get_sign() == selected_item)

        # Hiển thị hình ảnh và hướng dẫn
        pixmap = QPixmap(lesson.get_image_path())
        self.image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        self.instruction_label.setText(lesson.get_instruction())
    def capture_image_and_predict(self):
        """Chụp ảnh từ camera và dự đoán ký hiệu"""
        try:
            img = self.image_analyzer.capture_image()
            if img is not None:
                predicted_label = self.image_analyzer.predict(img)
                if predicted_label is None:
                    QMessageBox.warning(self, "Lỗi", "Không thể thực hiện dự đoán!")
                    return

                actual_label = self.lesson_list.currentItem().text().split(" - ")[0]
                accuracy = self.image_analyzer.evaluate_prediction(actual_label, predicted_label)

                # Lưu phản hồi và tiến trình học tập
                self.feedback.give_feedback(actual_label, predicted_label)
                self.progress_tracker.update_progress(actual_label, accuracy)

                # Hiển thị kết quả cho người dùng
                QMessageBox.information(self, "Kết quả",
                                        f"Ký hiệu thực tế: {actual_label}\n"
                                        f"Ký hiệu dự đoán: {predicted_label}\n"
                                        f"Độ chính xác: {'Đúng' if accuracy else 'Sai'}")
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể khởi động camera hoặc chụp ảnh từ camera!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi thực hiện dự đoán: {str(e)}")

    def display_progress(self):
        """Hiển thị tiến trình học tập"""
        report = self.progress_tracker.get_progress_report()
        history = self.feedback.get_feedback_history()

        QMessageBox.information(self, "Tiến trình học tập", "\n".join(report + history))

# ----------------------------------------------------
# Lớp Feedback
class Feedback:
    def __init__(self, username, feedback_file="learning/user_feedback.json"):
        self.username = username
        self.feedback_file = feedback_file
        self.feedback_data = self.load_feedback_data()

    def load_feedback_data(self):
        """Tải phản hồi từ file JSON, tạo file mới nếu không tồn tại"""
        if not os.path.exists(self.feedback_file):
            # Tạo tệp mới với dữ liệu rỗng nếu chưa tồn tại
            print(f"File {self.feedback_file} không tồn tại. Tạo file mới.")
            with open(self.feedback_file, 'w') as file:
                json.dump({}, file)
            return {}

        try:
            with open(self.feedback_file, 'r') as file:
                all_feedback = json.load(file)
                return all_feedback.get(self.username, {})
        except json.JSONDecodeError:
            print(f"File JSON bị hỏng: {self.feedback_file}")
            return {}
        except Exception as e:
            print(f"Lỗi khi tải phản hồi người dùng: {e}")
            return {}
    def save_feedback_data(self):
        """Lưu phản hồi người dùng vào file JSON"""
        try:
            with open(self.feedback_file, 'r') as file:
                all_feedback = json.load(file)
        except FileNotFoundError:
            all_feedback = {}  # Nếu file không tồn tại, tạo dict trống
        except Exception as e:
            print(f"Lỗi khi tải phản hồi người dùng: {e}")
            all_feedback = {}

        all_feedback[self.username] = self.feedback_data

        try:
            with open(self.feedback_file, 'w') as file:
                json.dump(all_feedback, file, indent=4)
            print("Phản hồi của người dùng đã được lưu.")
        except Exception as e:
            print(f"Lỗi khi lưu phản hồi: {e}")


    def give_feedback(self, actual_label, predicted_label):
        """Ghi nhận phản hồi dựa trên kết quả dự đoán"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feedback_entry = {
            'timestamp': timestamp,
            'actual': actual_label,
            'predicted': predicted_label,
            'correct': actual_label == predicted_label,
        }

        if actual_label == predicted_label:
            feedback_entry['suggestion'] = "Ký hiệu đúng. Tiếp tục luyện tập để duy trì phong độ!"
        else:
            feedback_entry['suggestion'] = "Ký hiệu sai. Cần thực hiện động tác chính xác hơn."

        self.feedback_data[timestamp] = feedback_entry
        self.save_feedback_data()

    def get_feedback_history(self):
        """Lấy lịch sử phản hồi"""
        history = [
            f"Thời gian: {entry['timestamp']}, Thực tế: {entry['actual']}, Dự đoán: {entry['predicted']}, "
            f"Đúng/Sai: {'Đúng' if entry['correct'] else 'Sai'}, Gợi ý: {entry['suggestion']}"
            for entry in self.feedback_data.values()
        ]
        return history

# ----------------------------------------------------
# Lớp Lesson và LessonManager
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
        """Tải dữ liệu bài học từ file JSON, tạo file mới nếu không tồn tại"""
        if not os.path.exists(self.lessons_file):
            # Tạo file mới với dữ liệu rỗng nếu không tồn tại
            print(f"File {self.lessons_file} không tồn tại. Tạo file mới.")
            with open(self.lessons_file, 'w') as file:
                json.dump([], file)  # Tạo danh sách rỗng trong file JSON
            return []

        try:
            with open(self.lessons_file, 'r') as file:
                lessons_data = json.load(file)
                return [Lesson(**lesson) for lesson in lessons_data]
        except json.JSONDecodeError:
            print(f"File JSON bị hỏng: {self.lessons_file}")
            return []
        except Exception as e:
            print(f"Lỗi khi tải bài học: {e}")
            return []

    def save_lessons(self):
        """Lưu dữ liệu bài học vào file JSON"""
        lessons_data = {}
        for lesson in self.lessons:
            if lesson.get_level() not in lessons_data:
                lessons_data[lesson.get_level()] = {}
            lessons_data[lesson.get_level()][lesson.get_sign()] = lesson.get_instruction()

        try:
            with open(self.lessons_file, 'w') as file:
                json.dump(lessons_data, file, indent=4)
            print("Dữ liệu bài học đã được lưu.")
        except Exception as e:
            print(f"Lỗi khi lưu bài học: {e}")

    def add_lesson(self, sign, instruction, level="Cơ bản", image_path=None):
        """Thêm bài học mới"""
        lesson = Lesson(sign, instruction, level, image_path)
        self.lessons.append(lesson)
        self.save_lessons()

    def get_lessons_by_level(self, level):
        return [lesson for lesson in self.lessons if lesson.get_level() == level]

    def get_lessons(self):
        return self.lessons

# ----------------------------------------------------
# Lớp ProgressTracker
class ProgressTracker:
    def __init__(self, username, progress_file="learning/user_progress.json"):
        self.username = username
        self.progress_file = progress_file
        self.progress_data = self.load_progress_data()

    def load_progress_data(self):
        """Tải dữ liệu tiến trình học tập từ file JSON, tạo file mới nếu không tồn tại"""
        if not os.path.exists(self.progress_file):
            # Tạo file mới với dữ liệu rỗng nếu chưa tồn tại
            print(f"File {self.progress_file} không tồn tại. Tạo file mới.")
            with open(self.progress_file, 'w') as file:
                json.dump({}, file)
            return {}

        try:
            with open(self.progress_file, 'r') as file:
                all_progress = json.load(file)
                return all_progress.get(self.username, {})
        except json.JSONDecodeError:
            print(f"File JSON bị hỏng: {self.progress_file}")
            return {}
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu tiến trình: {e}")
            return {}

    def save_progress_data(self):
        """Lưu dữ liệu tiến trình học tập vào file JSON"""
        try:
            with open(self.progress_file, 'r') as file:
                all_progress = json.load(file)
        except FileNotFoundError:
            all_progress = {}
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu tiến trình: {e}")
            all_progress = {}

        all_progress[self.username] = self.progress_data

        try:
            with open(self.progress_file, 'w') as file:
                json.dump(all_progress, file, indent=4)
            print("Dữ liệu tiến trình đã được lưu.")
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu tiến trình: {e}")

    def update_progress(self, actual_label, accuracy):
        """Cập nhật dữ liệu tiến trình học tập"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.progress_data[timestamp] = {
            'actual_label': actual_label,
            'accuracy': accuracy,
        }
        self.save_progress_data()

    def get_progress_report(self):
        """Tạo báo cáo tiến trình học tập"""
        report = [f"Thời gian: {time}, Ký hiệu thực tế: {data['actual_label']}, Độ chính xác: {data['accuracy']}"
                  for time, data in self.progress_data.items()]
        return report

# ----------------------------------------------------
# Lớp ImageAnalyzer (phân tích hình ảnh)
class ImageAnalyzer:
    def __init__(self, model_path):
        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        """Tải mô hình học máy từ tệp"""
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
            print("Mô hình đã được tải thành công.")
            return model
        else:
            print(f"Mô hình không tồn tại tại {model_path}")
            return None

    def predict(self, img):
        """Dự đoán ký hiệu từ hình ảnh"""
        if self.model is None:
            print("Mô hình chưa được tải. Không thể dự đoán.")
            return None

        processed_img = self.preprocess_image(img)
        prediction = self.model.predict(processed_img)
        predicted_label_index = np.argmax(prediction)

        try:
            label_map = {0: 'A', 1: 'B', 2: 'C'}  # Cập nhật cho phù hợp với mô hình của bạn
            predicted_label = label_map[predicted_label_index]
            return predicted_label
        except KeyError:
            print(f"Chỉ số nhãn {predicted_label_index} không hợp lệ!")
            return None


    def capture_image(self):
        """Chụp ảnh từ camera"""
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("Không thể khởi động camera!")
            return None

        ret, frame = camera.read()
        camera.release()
        if ret:
            return frame
        else:
            print("Không thể chụp ảnh!")
            return None

    def preprocess_image(self, img):
        """Tiền xử lý hình ảnh trước khi dự đoán"""
        img_resized = cv2.resize(img, (64, 64))
        img_array = img_resized.astype("float32") / 255.0
        return np.expand_dims(img_array, axis=0)

    def evaluate_prediction(self, actual_label, predicted_label):
        """Đánh giá độ chính xác của dự đoán"""
        return actual_label == predicted_label

    def display_instruction(self, image_path):
        """Hiển thị hình ảnh hướng dẫn."""
        img = plt.imread(image_path)
        plt.imshow(img)
        plt.axis('off')
        plt.show()

# ----------------------------------------------------
# Hàm khởi động quá trình học
def start_learning(username):
    lesson_manager = LessonManager()
    feedback = Feedback(username)
    image_analyzer = ImageAnalyzer(r"C:\Users\ASUS\Downloads\sign-languge-recognise-v2\app\data\saved_models\cnn_model_best.keras")

    # Thêm bài học ví dụ
    lessons_data = [
        # Các số từ 0-9
        ("0", "Giơ bàn tay và nắm các ngón tay lại thành hình số 0.", "Cơ bản", "images/0.png"),
        ("1", "Giơ một ngón tay lên.", "Cơ bản", "images/1.png"),
        ("2", "Giơ hai ngón tay lên.", "Cơ bản", "images/2.png"),
        ("3", "Giơ ba ngón tay lên.", "Cơ bản", "images/3.png"),
        ("4", "Giơ bốn ngón tay lên.", "Cơ bản", "images/4.png"),
        ("5", "Giơ cả bàn tay lên với các ngón tay mở rộng.", "Cơ bản", "images/5.png"),
        ("6", "Giơ ngón tay cái và ngón út lên.", "Cơ bản", "images/6.png"),
        ("7", "Giơ ngón cái, ngón út và ngón trỏ lên.", "Cơ bản", "images/7.png"),
        ("8", "Giơ ngón tay cái và ngón trỏ lên tạo thành hình số 8.", "Cơ bản", "images/8.png"),
        ("9", "Giơ các ngón tay tạo thành hình số 9.", "Cơ bản", "images/9.png"),
        ("A", "Giơ tay với các ngón tay nắm lại tạo thành hình chữ A.", "Cơ bản", "images/10.png"),
        ("B", "Giơ tay với các ngón tay duỗi thẳng, bàn tay mở ra.", "Cơ bản", "images/11.png"),
        ("C", "Giơ tay tạo hình chữ C.", "Cơ bản", "images/12.png"),
        ("D", "Giơ tay với ngón trỏ duỗi thẳng, các ngón còn lại nắm lại.", "Cơ bản", "images/13.png"),
        ("E", "Giơ tay nắm lại nhưng ngón cái đặt ở phía trên.", "Cơ bản", "images/14.png"),
        ("F", "Giơ tay với ngón cái và ngón trỏ tạo thành vòng tròn.", "Cơ bản", "images/15.png"),
        ("G", "Giơ tay với ngón cái và ngón trỏ giơ ngang.", "Cơ bản", "images/16.png"),
        ("H", "Giơ tay với hai ngón tay giơ thẳng ra.", "Cơ bản", "images/17.png"),
        ("I", "Giơ tay với ngón út giơ ra.", "Cơ bản", "images/18.png"),
        ("J", "Giơ tay với ngón út vẽ một đường cong như chữ J.", "Cơ bản", "images/19.png"),
        ("K", "Giơ tay với ngón cái nắm lại, ngón trỏ và ngón giữa duỗi thẳng.", "Cơ bản", "images/20.png"),
        ("L", "Giơ tay tạo hình chữ L.", "Cơ bản", "images/21.png"),
        ("M", "Giơ tay với ngón tay cái nắm lại bên dưới các ngón tay khác.", "Cơ bản", "images/22.png"),
        ("N", "Giơ tay với ngón tay cái nắm bên dưới hai ngón tay đầu.", "Cơ bản", "images/23.png"),
        ("O", "Giơ tay tạo hình chữ O.", "Cơ bản", "images/24.png"),
        ("P", "Giơ tay tạo hình chữ P.", "Cơ bản", "images/25.png"),
        ("Q", "Giơ tay tạo hình chữ Q.", "Cơ bản", "images/26.png"),
        ("R", "Giơ tay với hai ngón tay bắt chéo nhau.", "Cơ bản", "images/27.png"),
        ("S", "Giơ tay nắm lại với ngón cái đặt lên phía trên.", "Cơ bản", "images/28.png"),
        ("T", "Giơ tay với ngón cái kẹp giữa ngón trỏ và ngón giữa.", "Cơ bản", "images/29.png"),
        ("U", "Giơ tay với hai ngón tay duỗi thẳng.", "Cơ bản", "images/30.png"),
        ("V", "Giơ tay tạo hình chữ V.", "Cơ bản", "images/31.png"),
        ("W", "Giơ tay với ba ngón tay giơ thẳng ra tạo hình chữ W.", "Cơ bản", "images/32.png"),
        ("X", "Giơ tay với ngón trỏ gập lại tạo hình chữ X.", "Cơ bản", "images/33.png"),
        ("Y", "Giơ tay với ngón cái và ngón út duỗi thẳng.", "Cơ bản", "images/34.png"),
        ("Z", "Giơ ngón trỏ lên và vẽ một đường zic-zac tạo hình chữ Z.", "Cơ bản", "images/35.png"),
    ]

    for lesson in lessons_data:
        lesson_manager.add_lesson(*lesson)

    lessons = lesson_manager.get_lessons()

    # Hiển thị danh sách bài học
    for lesson in lessons:
        print(f"Cấp độ: {lesson.get_level()} - Ký hiệu: {lesson.get_sign()} - Hướng dẫn: {lesson.get_instruction()}")
    
    # Giả sử người dùng chọn một bài học
    selected_lesson = lessons[0]

    image_analyzer.display_instruction(selected_lesson.get_image_path())

    img = image_analyzer.capture_image()
    if img is not None:
        predicted_label = image_analyzer.predict(img)

        accuracy = image_analyzer.evaluate_prediction(selected_lesson.get_sign(), predicted_label)

        feedback.give_feedback(selected_lesson.get_sign(), predicted_label)

        print(f"Độ chính xác: {accuracy}")

if __name__ == "__main__":
    start_learning("user123")
