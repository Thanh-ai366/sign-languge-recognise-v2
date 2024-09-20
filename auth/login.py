import bcrypt
import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

class UserManager:
    def __init__(self):
        self.users = self.load_users()

    def load_users(self):
        # Giả lập dữ liệu người dùng từ file JSON hoặc cơ sở dữ liệu
        return {
            "user1": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "user2": bcrypt.hashpw("mypassword".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        }

    def login(self, username, password):
        if username not in self.users:
            return "Tên đăng nhập không tồn tại"
        
        stored_password_hash = self.users[username]
        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            token = self.create_jwt(username)
            return f"Token: {token}"
        else:
            return "Mật khẩu không đúng"

    def create_jwt(self, username):
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        payload = {
            'username': username,
            'exp': expiration_time
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token

    def verify_jwt(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload['username'], None
        except jwt.ExpiredSignatureError:
            return None, "Token đã hết hạn"
        except jwt.InvalidTokenError:
            return None, "Token không hợp lệ"

    def check_permission(self, username, required_role):
        # Giả lập kiểm tra quyền truy cập, có thể thay bằng truy vấn cơ sở dữ liệu
        user_roles = {
            "user1": "admin",
            "user2": "user"
        }
        if username in user_roles and user_roles[username] == required_role:
            return True
        return False
