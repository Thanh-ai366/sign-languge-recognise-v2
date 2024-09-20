import json
import os

class UserData:
    def __init__(self, username, data_file="auth/user_data.json"):
        self.username = username
        self.data_file = data_file
        self.data = self.load_user_data()

    def load_user_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    all_data = json.load(f)
                    return all_data.get(self.username, {})
            else:
                return {}
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu người dùng: {e}")
            return {}

    def save_user_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    all_data = json.load(f)
            else:
                all_data = {}

            all_data[self.username] = self.data

            with open(self.data_file, 'w') as f:
                json.dump(all_data, f)
            print("Dữ liệu người dùng đã được lưu.")
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu người dùng: {e}")

    def update_data(self, key, value):
        self.data[key] = value
        self.save_user_data()
