import tensorflow as tf

def save_model(model):
    file_path = r"C:\Users\ASUS\Downloads\sign-languge-recognise\app\data\saved_models\cnn_model_best.keras" 
    model.save(file_path)

def load_model():
    file_path = r"C:\Users\ASUS\Downloads\sign-languge-recognise\app\data\saved_models\cnn_model_best.keras"
    return tf.keras.models.load_model(file_path)
