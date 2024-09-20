import os
import cv2
import numpy as np

def create_directory(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Thư mục đã được tạo: {path}")
        else:
            print(f"Thư mục đã tồn tại: {path}")
    except Exception as e:
        print(f"Lỗi khi tạo thư mục {path}: {e}")

def preprocess_image(image_path, target_size=(64, 64)):
    try:
        # Đọc ảnh từ đường dẫn và chuyển sang grayscale
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Ảnh không tồn tại hoặc không thể đọc được: {image_path}")
        
        # Thay đổi kích thước ảnh và chuẩn hóa
        resized_image = cv2.resize(image, target_size)
        normalized_image = resized_image / 255.0
        return np.expand_dims(normalized_image, axis=-1)  # Thêm một chiều cho đầu vào mô hình
    except Exception as e:
        print(f"Lỗi khi tiền xử lý ảnh {image_path}: {e}")
        return None
