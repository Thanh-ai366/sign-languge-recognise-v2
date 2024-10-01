import unittest
import numpy as np
import time
from models.cnn_model import create_cnn_model

class TestModelPerformance(unittest.TestCase):
    def setUp(self):
        self.model = create_cnn_model()

    def test_model_prediction_time(self):
        # Tạo dữ liệu giả với kích thước lớn
        large_input = np.random.rand(1000, 64, 64, 1)
        
        # Đo thời gian dự đoán
        start_time = time.time()
        self.model.predict(large_input)
        end_time = time.time()

        prediction_time = end_time - start_time
        print(f"Thời gian dự đoán cho 1000 ảnh: {prediction_time:.2f} giây.")
        
        # Đảm bảo rằng thời gian dự đoán không quá lâu (ví dụ dưới 5 giây)
        self.assertLess(prediction_time, 5, "Mô hình quá chậm khi dự đoán.")

if __name__ == '__main__':
    unittest.main()
