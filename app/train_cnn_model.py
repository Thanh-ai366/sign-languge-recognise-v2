import os
import sys
import numpy as np
import logging
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from app.utils import preprocess_image, create_directory

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Đường dẫn tới thư mục dữ liệu và thư mục lưu trữ mô hình
processed_dir = "data/processed/"
model_path = "data/saved_models/cnn_model.h5"
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

def create_cnn_model(input_shape=(64, 64, 1), num_classes=36, optimizer='adam', learning_rate=0.001, dropout_rate=0.5):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(BatchNormalization())
    model.add(Dropout(dropout_rate))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(BatchNormalization())
    model.add(Dropout(dropout_rate))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(dropout_rate))
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(optimizer=Adam(learning_rate=learning_rate), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

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
    return np.array(augmented_data), np.array(augmented_labels)

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
model = create_cnn_model()

# Tạo callback cho Early Stopping và Learning Rate Scheduler
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3)
callbacks = [early_stopping, lr_scheduler]

# Huấn luyện mô hình
logger.info("Starting model training")
history = model.fit(
    X_train, y_train,
    epochs=20,
    validation_data=(X_test, y_test),
    callbacks=callbacks
)

# Lưu mô hình sau khi huấn luyện
model.save(model_path)
logger.info(f"Model saved to {model_path}")

# Ghi lại lịch sử huấn luyện
logger.info("Training history:")
for key in history.history.keys():
    logger.info(f"{key}: {history.history[key]}")
