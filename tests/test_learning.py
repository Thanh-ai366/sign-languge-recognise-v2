import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from app.learning import LearningApp, Feedback, LessonManager, ProgressTracker, ImageAnalyzer

class TestLearningApp(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.learning_app = LearningApp("test_user")

    def test_init(self):
        self.assertIsInstance(self.learning_app.lesson_manager, LessonManager)
        self.assertIsInstance(self.learning_app.feedback, Feedback)
        self.assertIsInstance(self.learning_app.image_analyzer, ImageAnalyzer)
        self.assertIsInstance(self.learning_app.progress_tracker, ProgressTracker)

    def test_display_lesson(self):
        mock_lesson = MagicMock()
        mock_lesson.get_sign.return_value = "A"
        mock_lesson.get_image_path.return_value = "test_image.png"
        mock_lesson.get_instruction.return_value = "Test instruction"
        
        self.learning_app.lesson_manager.get_lessons = MagicMock(return_value=[mock_lesson])
        self.learning_app.lesson_list.currentItem = MagicMock()
        self.learning_app.lesson_list.currentItem().text.return_value = "A - Basic"
        
        self.learning_app.display_lesson()
        
        self.assertEqual(self.learning_app.instruction_label.text(), "Test instruction")

    @patch('app.learning.ImageAnalyzer.capture_image')
    @patch('app.learning.ImageAnalyzer.predict')
    def test_capture_image_and_predict(self, mock_predict, mock_capture):
        mock_capture.return_value = MagicMock()
        mock_predict.return_value = "A"
        
        self.learning_app.lesson_list.currentItem = MagicMock()
        self.learning_app.lesson_list.currentItem().text.return_value = "A - Basic"
        
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            self.learning_app.capture_image_and_predict()
            mock_info.assert_called_once()

    def tearDown(self):
        self.app.quit()

class TestFeedback(unittest.TestCase):
    def setUp(self):
        self.feedback = Feedback("test_user")

    @patch('json.dump')
    @patch('json.load')
    def test_give_feedback(self, mock_load, mock_dump):
        mock_load.return_value = {}
        self.feedback.give_feedback("A", "A")
        mock_dump.assert_called_once()

    def test_get_feedback_history(self):
        self.feedback.feedback_data = {
            "2023-01-01 12:00:00": {
                "timestamp": "2023-01-01 12:00:00",
                "actual": "A",
                "predicted": "A",
                "correct": True,
                "suggestion": "Ký hiệu đúng. Tiếp tục luyện tập để duy trì phong độ!"
            }
        }
        history = self.feedback.get_feedback_history()
        self.assertEqual(len(history), 1)
        self.assertIn("Thời gian: 2023-01-01 12:00:00", history[0])

class TestLessonManager(unittest.TestCase):
    def setUp(self):
        self.lesson_manager = LessonManager()

    @patch('json.dump')
    def test_add_lesson(self, mock_dump):
        self.lesson_manager.add_lesson("A", "Test instruction", "Basic", "test_image.png")
        self.assertEqual(len(self.lesson_manager.lessons), 1)
        mock_dump.assert_called_once()

    def test_get_lessons_by_level(self):
        self.lesson_manager.lessons = [
            MagicMock(get_level=lambda: "Basic"),
            MagicMock(get_level=lambda: "Advanced")
        ]
        basic_lessons = self.lesson_manager.get_lessons_by_level("Basic")
        self.assertEqual(len(basic_lessons), 1)

class TestProgressTracker(unittest.TestCase):
    def setUp(self):
        self.progress_tracker = ProgressTracker("test_user")

    @patch('json.dump')
    @patch('json.load')
    def test_update_progress(self, mock_load, mock_dump):
        mock_load.return_value = {}
        self.progress_tracker.update_progress("A", True)
        mock_dump.assert_called_once()

    def test_get_progress_report(self):
        self.progress_tracker.progress_data = {
            "2023-01-01 12:00:00": {
                "lesson": "A",
                "accuracy": True,
                "timestamp": "2023-01-01 12:00:00"
            }
        }
        report = self.progress_tracker.get_progress_report()
        self.assertEqual(len(report), 1)
        self.assertIn("Buổi học: A", report[0])

class TestImageAnalyzer(unittest.TestCase):
    @patch('tensorflow.keras.models.load_model')
    def setUp(self, mock_load_model):
        self.image_analyzer = ImageAnalyzer("test_model_path")

    @patch('cv2.VideoCapture')
    def test_capture_image(self, mock_video_capture):
        mock_video_capture.return_value.read.return_value = (True, MagicMock())
        result = self.image_analyzer.capture_image()
        self.assertIsNotNone(result)

    @patch('cv2.cvtColor')
    @patch('cv2.resize')
    def test_preprocess_image(self, mock_resize, mock_cvtcolor):
        mock_image = MagicMock()
        result = self.image_analyzer.preprocess_image(mock_image)
        self.assertEqual(result.shape, (1, 64, 64, 1))

    @patch('numpy.argmax')
    def test_predict(self, mock_argmax):
        mock_argmax.return_value = 0
        mock_image = MagicMock()
        result = self.image_analyzer.predict(mock_image)
        self.assertEqual(result, "0")

    def test_evaluate_prediction(self):
        result = self.image_analyzer.evaluate_prediction("A", "A")
        self.assertTrue(result)
        result = self.image_analyzer.evaluate_prediction("A", "B")
        self.assertFalse(result)

