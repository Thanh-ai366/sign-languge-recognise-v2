import unittest
import numpy as np
from app.prediction import SignLanguagePredictor
from models.model_loader import load_model

class TestPrediction(unittest.TestCase):
    def setUp(self):
        self.model_path = "data/saved_models/cnn_model.pkl"
        self.labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        self.predictor = SignLanguagePredictor(self.model_path, self.labels_dict)

    def test_model_loading(self):
        model = load_model(self.model_path)
        self.assertIsNotNone(model, "Mô hình không được tải đúng cách.")

    def test_prediction_output(self):
        dummy_image = np.zeros((100, 100, 1))
        predicted_label = self.predictor.predict(dummy_image)
        self.assertIn(predicted_label, self.labels_dict.values(), "Dự đoán không hợp lệ.")

if __name__ == '__main__':
    unittest.main()
