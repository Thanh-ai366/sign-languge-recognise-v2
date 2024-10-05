import unittest
import numpy as np
import os
import tempfile
import csv
from unittest.mock import patch, MagicMock
from app.dataset_manager import DatasetManager
from app.utils import preprocess_image

class TestDatasetManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        self.processed_dir = os.path.join(self.temp_dir, 'processed')
        os.makedirs(self.data_dir)
        self.dataset_manager = DatasetManager(self.data_dir, self.processed_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        self.assertEqual(self.dataset_manager.data_dir, self.data_dir)
        self.assertEqual(self.dataset_manager.processed_dir, self.processed_dir)
        self.assertEqual(self.dataset_manager.test_size, 0.2)
        self.assertIsNone(self.dataset_manager.csv_file)

    @patch('app.dataset_manager.preprocess_image')
    def test_load_dataset_from_directory(self, mock_preprocess):
        mock_preprocess.return_value = np.zeros((64, 64, 1))
        os.makedirs(os.path.join(self.data_dir, 'A'))
        os.makedirs(os.path.join(self.data_dir, 'B'))
        open(os.path.join(self.data_dir, 'A', 'img1.png'), 'w').close()
        open(os.path.join(self.data_dir, 'B', 'img2.png'), 'w').close()

        data, labels = self.dataset_manager.load_dataset()

        self.assertEqual(len(data), 2)
        self.assertEqual(len(labels), 2)
        self.assertIn('A', labels)
        self.assertIn('B', labels)

    @patch('app.dataset_manager.preprocess_image')
    def test_load_dataset_from_csv(self, mock_preprocess):
        mock_preprocess.return_value = np.zeros((64, 64, 1))
        csv_file = os.path.join(self.temp_dir, 'data.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['img1.png', '0'])
            writer.writerow(['img2.png', '1'])
        
        open(os.path.join(self.data_dir, 'img1.png'), 'w').close()
        open(os.path.join(self.data_dir, 'img2.png'), 'w').close()

        self.dataset_manager.csv_file = csv_file
        data, labels = self.dataset_manager.load_dataset()

        self.assertEqual(len(data), 2)
        self.assertEqual(len(labels), 2)
        np.testing.assert_array_equal(labels, [0, 1])

    def test_load_dataset_csv_file_not_found(self):
        self.dataset_manager.csv_file = 'non_existent.csv'
        data, labels = self.dataset_manager.load_dataset()
        self.assertIsNone(data)
        self.assertIsNone(labels)

    @patch('app.dataset_manager.preprocess_image')
    def test_load_dataset_image_not_found(self, mock_preprocess):
        mock_preprocess.return_value = None
        os.makedirs(os.path.join(self.data_dir, 'A'))
        open(os.path.join(self.data_dir, 'A', 'img1.png'), 'w').close()

        data, labels = self.dataset_manager.load_dataset()

        self.assertEqual(len(data), 0)
        self.assertEqual(len(labels), 0)

    def test_augment_dataset(self):
        data = np.random.rand(10, 64, 64, 1)
        labels = np.array(['A'] * 5 + ['B'] * 5)

        augmented_data, augmented_labels = self.dataset_manager.augment_dataset(data, labels)

        self.assertEqual(len(augmented_data), 50)  # 10 original * 5 augmentations
        self.assertEqual(len(augmented_labels), 50)
        self.assertEqual(list(augmented_labels).count('A'), 25)
        self.assertEqual(list(augmented_labels).count('B'), 25)

    def test_augment_dataset_empty_input(self):
        data = np.array([])
        labels = np.array([])

        augmented_data, augmented_labels = self.dataset_manager.augment_dataset(data, labels)

        self.assertEqual(len(augmented_data), 0)
        self.assertEqual(len(augmented_labels), 0)

if __name__ == '__main__':
    unittest.main()
