import unittest
import os
import json
from auth.user_data import UserData

class TestUserData(unittest.TestCase):
    def setUp(self):
        self.user_data = UserData("test_user")
        self.test_data_file = self.user_data.user_file

    def tearDown(self):
        # Xóa file dữ liệu sau khi kiểm tra
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def test_update_and_get_user_data(self):
        self.user_data.update_user_data("progress", {"A": 0.95})
        progress = self.user_data.get_user_data("progress")
        self.assertEqual(progress["A"], 0.95, "Dữ liệu người dùng không được lưu hoặc truy xuất đúng cách.")

if __name__ == '__main__':
    unittest.main()
