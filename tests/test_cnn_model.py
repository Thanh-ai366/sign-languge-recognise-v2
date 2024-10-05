import unittest
import numpy as np
import tensorflow as tf
from app.models.cnn_model import create_cnn_model

class TestCNNModel(unittest.TestCase):
    def setUp(self):
        self.model = create_cnn_model()

    def test_model_structure(self):
        self.assertIsInstance(self.model, tf.keras.models.Sequential)
        self.assertEqual(len(self.model.layers), 13)

    def test_input_shape(self):
        self.assertEqual(self.model.input_shape, (None, 64, 64, 1))

    def test_output_shape(self):
        self.assertEqual(self.model.output_shape, (None, 36))

    def test_model_compilation(self):
        self.assertIsNotNone(self.model.optimizer)
        self.assertIsInstance(self.model.optimizer, tf.keras.optimizers.Adam)
        self.assertEqual(self.model.loss, 'categorical_crossentropy')
        self.assertEqual(self.model.metrics[0], 'accuracy')

    def test_custom_input_shape(self):
        custom_model = create_cnn_model(input_shape=(32, 32, 3))
        self.assertEqual(custom_model.input_shape, (None, 32, 32, 3))

    def test_custom_num_classes(self):
        custom_model = create_cnn_model(num_classes=10)
        self.assertEqual(custom_model.output_shape, (None, 10))

    def test_model_prediction(self):
        rng = np.random.default_rng()
        dummy_input = rng.random((1, 64, 64, 1))
        prediction = self.model.predict(dummy_input)
        self.assertEqual(prediction.shape, (1, 36))
        self.assertAlmostEqual(np.sum(prediction), 1.0, places=6)

    def test_model_training(self):
        dummy_x = np.random.rand(10, 64, 64, 1)
        dummy_y = np.eye(36)[np.random.randint(0, 36, 10)]
        history = self.model.fit(dummy_x, dummy_y, epochs=1, verbose=0)
        self.assertIn('loss', history.history)
        self.assertIn('accuracy', history.history)

    def test_layer_types(self):
        expected_layer_types = [
            tf.keras.layers.Conv2D,
            tf.keras.layers.BatchNormalization,
            tf.keras.layers.MaxPooling2D,
            tf.keras.layers.Conv2D,
            tf.keras.layers.BatchNormalization,
            tf.keras.layers.MaxPooling2D,
            tf.keras.layers.Conv2D,
            tf.keras.layers.BatchNormalization,
            tf.keras.layers.MaxPooling2D,
            tf.keras.layers.Flatten,
            tf.keras.layers.Dense,
            tf.keras.layers.Dropout,
            tf.keras.layers.Dense
        ]
        for layer, expected_type in zip(self.model.layers, expected_layer_types):
            self.assertIsInstance(layer, expected_type)

    def test_dropout_rate(self):
        dropout_layer = self.model.layers[-2]
        self.assertIsInstance(dropout_layer, tf.keras.layers.Dropout)
        self.assertEqual(dropout_layer.rate, 0.5)

if __name__ == '__main__':
    unittest.main()
