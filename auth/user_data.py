import json
import os

class UserData:
    def __init__(self, username, data_dir="data/user_data/"):
        self.username = username
        self.data_dir = data_dir
        self.user_file = os.path.join(data_dir, f"{username}_data.json")
        self.data = self.load_user_data()

    def load_user_data(self):
        if os.path.exists(self.user_file):
            with open(self.user_file, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_user_data(self):
        with open(self.user_file, 'w') as file:
            json.dump(self.data, file, indent=4)

    def update_user_data(self, key, value):
        self.data[key] = value
        self.save_user_data()

    def get_user_data(self, key):
        return self.data.get(key, None)

# Sử dụng UserData để lưu trữ và truy xuất dữ liệu cá nhân
if __name__ == "__main__":
    user_data = UserData("new_user")
    user_data.update_user_data("progress", {"A": 0.95, "B": 0.85})
    print(user_data.get_user_data("progress"))
