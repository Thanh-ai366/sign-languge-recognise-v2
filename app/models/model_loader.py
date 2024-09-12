import tensorflow as tf

def save_model(model, file_path):
    model.save(file_path)  # Lưu toàn bộ mô hình

def load_model(file_path):
    return tf.keras.models.load_model(file_path)  # Tải lại toàn bộ mô hình

