import os
import csv
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from app.utils import create_directory, preprocess_image

class DatasetManager:
    def __init__(self, data_dir, processed_dir, csv_file=None, test_size=0.2):
        self.data_dir = data_dir
        self.processed_dir = processed_dir
        self.csv_file = csv_file
        self.test_size = test_size
        create_directory(self.processed_dir)

        self.datagen = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.1,
            zoom_range=0.1,
            horizontal_flip=True,
            fill_mode='nearest'
        )

    def load_dataset(self):
        data = []
        labels = []
        if self.csv_file:
            try:
                with open(self.csv_file, 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        img_path = os.path.join(self.data_dir, row[0])
                        label = int(row[1])
                        if os.path.exists(img_path):
                            img = preprocess_image(img_path, size=(64, 64))
                            data.append(img)
                            labels.append(label)
                        else:
                            print(f"Ảnh không tồn tại: {img_path}")
                return np.array(data), np.array(labels)
            except Exception as e:
                print(f"Lỗi khi tải dữ liệu từ CSV: {e}")
                return None, None
        else:
            for label in os.listdir(self.data_dir):
                label_dir = os.path.join(self.data_dir, label)
                if os.path.isdir(label_dir):
                    for img_file in os.listdir(label_dir):
                        img_path = os.path.join(label_dir, img_file)
                        image = preprocess_image(img_path, size=(64, 64))
                        data.append(image)
                        labels.append(label)
            return np.array(data), np.array(labels)

    def augment_dataset(self, data, labels):
        augmented_data = []
        augmented_labels = []
        for i in range(len(data)):
            img = data[i].reshape((1, 64, 64, 1))
            for _ in range(5):
                aug_iter = self.datagen.flow(img, batch_size=1)
                aug_img = next(aug_iter).reshape((64, 64, 1))
                augmented_data.append(aug_img)
                augmented_labels.append(labels[i])
        return np.array(augmented_data), np.array(augmented_labels)

    def split_dataset(self, data, labels):
        X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=self.test_size, stratify=labels)
        return X_train, X_test, y_train, y_test

    def save_processed_dataset(self, X_train, X_test, y_train, y_test):
        np.save(os.path.join(self.processed_dir, 'X_train.npy'), X_train)
        np.save(os.path.join(self.processed_dir, 'X_test.npy'), X_test)
        np.save(os.path.join(self.processed_dir, 'y_train.npy'), y_train)
        np.save(os.path.join(self.processed_dir, 'y_test.npy'), y_test)
        print("Dữ liệu đã được lưu thành công!")

    def load_processed_dataset(self):
        try:
            X_train = np.load(os.path.join(self.processed_dir, 'X_train.npy'))
            X_test = np.load(os.path.join(self.processed_dir, 'X_test.npy'))
            y_train = np.load(os.path.join(self.processed_dir, 'y_train.npy'))
            y_test = np.load(os.path.join(self.processed_dir, 'y_test.npy'))
            return X_train, X_test, y_train, y_test
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu đã xử lý: {e}")
            return None, None