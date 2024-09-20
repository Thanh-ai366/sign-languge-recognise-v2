import bcrypt
import json

class Register:
    def __init__(self):
        self.users_file = 'auth/users.json'
        self.load_users()

    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f)

    def register(self, username, password):
        if username in self.users:
            return "Tên người dùng đã tồn tại"

        if not self.is_password_valid(password):
            return "Mật khẩu không hợp lệ: phải có ít nhất 8 ký tự, bao gồm chữ cái và số, ký tự đặc biệt"

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.users[username] = password_hash
        self.save_users()
        return "Đăng ký thành công"

    def is_password_valid(self, password):
        if len(password) < 8:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isalpha() for char in password):
            return False
        if not any(char in "!@#$%^&*()-_+=" for char in password):
            return False
        return True
