import bcrypt
import json
import os
import jwt
from datetime import datetime, timedelta

# Khóa bảo mật cho JWT (lưu trữ ở nơi an toàn)
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")

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
            # Đăng nhập thành công, tạo JWT
            token = self.create_jwt(username)
            return f"Đăng nhập thành công! Token: {token}"
        else:
            return "Mật khẩu không chính xác."

    def create_jwt(self, username):
        # Tạo JWT với thời gian hết hạn 1 giờ
        payload = {
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=1)  # Token hết hạn sau 1 giờ
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def verify_jwt(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload["username"]
        except jwt.ExpiredSignatureError:
            return "Token đã hết hạn."
        except jwt.InvalidTokenError:
            return "Token không hợp lệ."

# Sử dụng UserManager để đăng nhập và xác thực
if __name__ == "__main__":
    user_manager = UserManager()
    response = user_manager.login("new_user", "secure_password")
    print(response)
    
    # Ví dụ kiểm tra token
    token = response.split("Token: ")[1]  # Lấy token từ chuỗi phản hồi
    print(user_manager.verify_jwt(token))
