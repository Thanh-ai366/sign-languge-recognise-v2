import os
import sys
import numpy as np
import logging
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.cnn_model import create_cnn_model
from models.model_loader import save_model
from app.utils import preprocess_image, create_directory

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Đường dẫn tới thư mục dữ liệu và thư mục lưu trữ mô hình
processed_dir = "data/processed/"
model_path = "data/saved_models/cnn_model.h5"  # Đổi đuôi mở rộng sang .h5

# Tạo thư mục lưu trữ mô hình đã huấn luyện nếu chưa tồn tại
create_directory(os.path.dirname(model_path))

# Tạo ImageDataGenerator cho Data Augmentation
datagen = ImageDataGenerator(
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Ánh xạ nhãn từ ký tự thành số (0-9 cho số, 10-35 cho chữ cái)
label_mapping = {str(i): i for i in range(10)}  # Ánh xạ từ 0 đến 9 cho số
label_mapping.update({chr(97 + i): 10 + i for i in range(26)})  # Ánh xạ từ a đến z (10 -> a, 35 -> z)

def load_dataset():
    data = []
    labels = []
    for label in os.listdir(processed_dir):
        label_dir = os.path.join(processed_dir, label)
        if os.path.isdir(label_dir):
            try:
                label_id = int(label)  # Chuyển đổi nhãn thành số nguyên
            except ValueError:
                logger.warning(f"Skipping invalid label: {label}")
                continue

            for img_file in os.listdir(label_dir):
                img_path = os.path.join(label_dir, img_file)
                logger.info(f"Processing image: {img_path}")
                image = preprocess_image(img_path, size=(64, 64))
                data.append(image)
                labels.append(label_id)
    data = np.array(data)
    labels = np.array(labels)
    logger.info(f"Loaded {len(data)} samples")
    return data, labels

def augment_dataset(data, labels):
    augmented_data = []
    augmented_labels = []
    for i in range(len(data)):
        img = data[i].reshape((1, 64, 64, 1))
        for _ in range(5):  # Tạo thêm 5 biến thể của mỗi hình ảnh
            aug_iter = datagen.flow(img, batch_size=1)
            aug_img = next(aug_iter).reshape((64, 64, 1))
            augmented_data.append(aug_img)
            augmented_labels.append(labels[i])
    augmented_data = np.array(augmented_data)
    augmented_labels = np.array(augmented_labels)
    logger.info(f"Augmented dataset to {len(augmented_data)} samples")
    return augmented_data, augmented_labels

# Tải và chuẩn bị dữ liệu
data, labels = load_dataset()
if len(data) == 0:
    raise ValueError("No data loaded. Please check the data directory.")

data, labels = augment_dataset(data, labels)

# Chuyển đổi nhãn sang dạng one-hot encoding
labels = to_categorical(labels, num_classes=36)

# Chia dữ liệu thành tập huấn luyện và tập kiểm tra
X_train, X_test, y_train, y_test = train_test_split(
    data, labels, test_size=0.2, stratify=labels.argmax(axis=1)
)
logger.info(f"Training data shape: {X_train.shape}, Test data shape: {X_test.shape}")

# Tạo mô hình CNN
model = create_cnn_model(input_shape=(64, 64, 1), num_classes=36)

# Huấn luyện mô hình
logger.info("Starting model training")
history = model.fit(X_train, y_train, epochs=20, validation_data=(X_test, y_test))

# Lưu mô hình sau khi huấn luyện
save_model(model, model_path)
logger.info(f"Model saved to {model_path}")

# Ghi lại lịch sử huấn luyện
logger.info("Training history:")
for key in history.history.keys():
    logger.info(f"{key}: {history.history[key]}")
