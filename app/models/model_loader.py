import pickle

def save_model(model, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(model, file)

def load_model(file_path):
    with open(file_path, 'rb') as file:
        model = pickle.load(file)
    return model
