import os
import sys
import numpy as np
import logging
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.cnn_model import create_cnn_model
from models.model_loader import save_model
from app.utils import preprocess_image, create_directory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

processed_dir = "data/processed/"
model_path = "data/saved_models/cnn_model_best.keras"
create_directory(os.path.dirname(model_path))

def load_dataset():
    data = []
    labels = []
    for label in os.listdir(processed_dir):
        label_dir = os.path.join(processed_dir, label)
        if os.path.isdir(label_dir):
            try:
                label_id = int(label)
            except ValueError:
                logger.warning(f"Bỏ qua nhãn không hợp lệ: {label}")
                continue

            for img_file in os.listdir(label_dir):
                img_path = os.path.join(label_dir, img_file)
                logger.info(f"Đang xử lý ảnh: {img_path}")
                image = preprocess_image(img_path, size=(64, 64))
                if image is not None:
                    data.append(image)
                    labels.append(label_id)
                else:
                    logger.warning(f"Không thể xử lý ảnh: {img_path}")

    data = np.array(data)
    labels = np.array(labels)

    if len(data) == 0:
        raise ValueError("Không có dữ liệu nào được tải. Vui lòng kiểm tra thư mục dữ liệu.")
    
    logger.info(f"Tải thành công {len(data)} mẫu.")
    return data, labels

def augment_dataset(data, labels, batch_size=1000):
    augmented_data = []
    augmented_labels = []
    datagen = ImageDataGenerator(
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    for i in range(0, len(data), batch_size):
        batch_data = data[i:i + batch_size]
        batch_labels = labels[i:i + batch_size]
        
        for j in range(len(batch_data)):
            img = batch_data[j].reshape((1, 64, 64, 1))
            for _ in range(5):
                aug_iter = datagen.flow(img, batch_size=1)
                aug_img = next(aug_iter).reshape((64, 64, 1))
                augmented_data.append(aug_img)
                augmented_labels.append(batch_labels[j])
    
    return np.array(augmented_data), np.array(augmented_labels)

def train_model():
    data, labels = load_dataset()
    data, labels = augment_dataset(data, labels)
    labels = to_categorical(labels, num_classes=36)

    train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size=0.2, stratify=labels.argmax(axis=1), random_state=42)

    logger.info(f"Dữ liệu huấn luyện: {train_data.shape}, Dữ liệu kiểm tra: {test_data.shape}")

    model = create_cnn_model(input_shape=(64, 64, 1), num_classes=36)

    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3)
    checkpoint = ModelCheckpoint('saved_models/cnn_model_best.keras', monitor='val_loss', save_best_only=True)

    logger.info("Bắt đầu huấn luyện mô hình")
    history = model.fit(train_data, train_labels, epochs=20, validation_data=(test_data, test_labels), callbacks=[early_stopping, lr_scheduler, checkpoint])

    save_model(model, model_path)
    logger.info(f"Mô hình đã được lưu vào {model_path}")

    logger.info("Lịch sử huấn luyện:")
    for key in history.history.keys():

        logger.info(f"{key}: {history.history[key]}")
if __name__ == "__main__":
    train_model()
