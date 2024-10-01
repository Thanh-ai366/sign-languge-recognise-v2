import unittest
from models.cnn_model import create_cnn_model

class TestModels(unittest.TestCase):
    def test_cnn_model_creation(self):
        model = create_cnn_model()
        self.assertIsNotNone(model, "Mô hình CNN không được khởi tạo thành công.")
        self.assertEqual(len(model.layers), 8, "Số tầng của mô hình CNN không đúng.")
    
    def test_cnn_model_compilation(self):
        model = create_cnn_model()
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        self.assertIsNotNone(model.optimizer, "Mô hình CNN chưa được compile đúng cách.")

if __name__ == '__main__':
    unittest.main()
