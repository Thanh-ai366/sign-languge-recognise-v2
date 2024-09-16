import bcrypt
import json
import os

class Register:
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

    def register(self, username, password):
        if username in self.users:
            return "Tên người dùng đã tồn tại."
        
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.users[username] = {"password": hashed_password, "data": {}}
        self.save_users()
        return "Đăng ký thành công!"

# Sử dụng Register để đăng ký người dùng mới
if __name__ == "__main__":
    user_manager = Register()
    response = user_manager.register("new_user", "secure_password")
    print(response)
