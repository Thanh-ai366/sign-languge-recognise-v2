import unittest
import numpy as np
from app.prediction import SignLanguagePredictor
from models.model_loader import load_model

class TestSignLanguagePredictor(unittest.TestCase):
    def setUp(self):
        from unittest.mock import MagicMock
        self.model_path = "data/saved_models/cnn_model.pkl"
        self.labels_dict = {i: chr(97 + i) for i in range(26)}
        self.labels_dict.update({i + 26: str(i) for i in range(10)})
        self.parent_window = MagicMock()
        self.predictor = SignLanguagePredictor(self.model_path, self.labels_dict, self.parent_window)

    def test_preprocess_frame(self):
        rng = np.random.default_rng(seed=42)
        dummy_frame = rng.random((100, 100, 3))
        processed_frame = self.predictor.preprocess_frame(dummy_frame)
        self.assertEqual(processed_frame.shape, (1, 4096))
        self.assertTrue(np.all(processed_frame >= 0) and np.all(processed_frame <= 1))

    def test_run_avg(self):
        rng = np.random.default_rng()
        image = rng.random((100, 100, 3))
        self.predictor.run_avg(image, 0.5)
        self.assertIsNotNone(self.predictor.bg)
        self.assertEqual(self.predictor.bg.shape, image.shape)

    def test_extract_hand(self):
        self.predictor.bg = np.zeros((100, 100, 3))
        image = np.ones((100, 100, 3)) * 255
        result = self.predictor.extract_hand(image)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)

    def test_predict_raises_exception(self):
        from app.exceptions import PredictionException
        self.predictor.model = MagicMock(side_effect=Exception("Prediction error"))
        with self.assertRaises(PredictionException):
            self.predictor.predict(np.zeros((1, 64, 64, 1)))

    def test_get_frame_raises_exception(self):
        from app.exceptions import WebcamOpenException
        self.predictor.cam = MagicMock()
        self.predictor.cam.read.return_value = (False, None)
        with self.assertRaises(WebcamOpenException):
            self.predictor.get_frame()

    def test_get_roi(self):
        rng = np.random.default_rng()
        frame = rng.random((480, 640, 3))
        roi = self.predictor.get_roi(frame)
        self.assertEqual(roi.shape, (250, 250, 3))

    def test_preprocess_image(self):
        roi = np.random.rand(250, 250, 3)
        processed = self.predictor.preprocess_image(roi)
        self.assertEqual(processed.shape, (250, 250))
        self.assertEqual(processed.dtype, np.uint8)

    def test_cleanup(self):
        self.predictor.cleanup()
        self.predictor.cam.release.assert_called_once()

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.main_window = MainWindow()

    def test_get_labels_dict(self):
        labels_dict = self.main_window.get_labels_dict()
        self.assertEqual(len(labels_dict), 36)
        self.assertEqual(labels_dict[0], 'a')
        self.assertEqual(labels_dict[35], '9')

    def tearDown(self):
        self.app.quit()

class TestPredictionWindow(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.parent_window = MagicMock()
        self.prediction_window = PredictionWindow(self.parent_window)

    def test_update_frame(self):
        rng = np.random.default_rng()
        frame = rng.integers(0, 255, (480, 640, 3), dtype=np.uint8)
        self.prediction_window.update_frame(frame)
        self.assertIsNotNone(self.prediction_window.video_label.pixmap())

    def test_stop_prediction(self):
        self.prediction_window.predictor = MagicMock()
        self.prediction_window.stop_prediction()
        self.assertFalse(self.prediction_window.predictor.running)
        self.prediction_window.predictor.cleanup.assert_called_once()

    def tearDown(self):
        self.app.quit()
