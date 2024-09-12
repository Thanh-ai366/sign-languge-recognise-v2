import unittest
import numpy as np
from learning.feedback import FeedbackSystem
from models.model_loader import load_model

class TestFeedbackSystem(unittest.TestCase):
    def setUp(self):
        self.model_path = "data/saved_models/cnn_model.h5"
        self.labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        self.feedback_system = FeedbackSystem(self.model_path, self.labels_dict)

    def test_evaluate_accuracy(self):
        dummy_image = np.zeros((64, 64, 1))
        correct_label = 0
        response = self.feedback_system.evaluate(dummy_image, correct_label)
        self.assertIn("Chính xác", response, "Phản hồi không hợp lệ.")

    def test_incorrect_label(self):
        dummy_image = np.zeros((64, 64, 1))
        correct_label = 1
        response = self.feedback_system.evaluate(dummy_image, correct_label)
        self.assertIn("Ký hiệu chưa chính xác", response, "Phản hồi không đưa ra gợi ý cải thiện.")

if __name__ == '__main__':
    unittest.main()
