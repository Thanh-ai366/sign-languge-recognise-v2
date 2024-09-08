import bcrypt
import json
import os

class UserManager:
    def __init__(self, user_db="data/users.json"):
        self.user_db = user_db
        self.load_users()

    def load_users(self):
        if os.path.exists(self.user_db):
            with open(self.user_db, 'r') as file:
                self.users = json.load(file)
        else:
            self.users = {}

    def save_users(self):
        with open(self.user_db, 'w') as file:
            json.dump(self.users, file, indent=4)

    def login(self, username, password):
        if username not in self.users:
            return "Tên người dùng không tồn tại."
        
        if bcrypt.checkpw(password.encode(), self.users[username]["password"].encode()):
            return "Đăng nhập thành công!"
        else:
            return "Mật khẩu không chính xác."

# Sử dụng UserManager để đăng nhập
if __name__ == "__main__":
    user_manager = UserManager()
    response = user_manager.login("new_user", "secure_password")
    print(response)
