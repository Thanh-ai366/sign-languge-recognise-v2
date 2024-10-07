import tensorflow as tf

def save_model(model, file_path=None):
    if file_path is None:
        file_path = r"C:\Users\ASUS\Downloads\sign-languge-recognise-v2\app\data\saved_models\cnn_model_best.keras" 
    model.save(file_path)

def load_model(model_path=None):
    if model_path is None:
        model_path = r"C:\Users\ASUS\Downloads\sign-languge-recognise-v2\app\data\saved_models\cnn_model_best.keras"
    return tf.keras.models.load_model(model_path)
