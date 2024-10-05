import os
import threading
import jwt
import json
import datetime
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QApplication
)
from PyQt5.QtCore import pyqtSignal
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from argon2 import PasswordHasher, exceptions as argon2_exceptions
import redis


# Khởi tạo Redis để lưu trữ token blacklist
r = redis.Redis(host='localhost', port=6379, db=0)


# Thêm token vào blacklist
def blacklist_token(jti):
    r.set(jti, 'blacklisted', ex=timedelta(hours=1))


# Kiểm tra xem token có trong blacklist không
def is_token_blacklisted(jti):
    return r.get(jti) is not None


# Cấu hình SQLAlchemy
Base = declarative_base()
engine = create_engine('sqlite:///data/users.db')
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    hashed_password = Column(String)
    email = Column(String)
    created_at = Column(DateTime)


# Khởi tạo bảng trong database nếu chưa tồn tại
Base.metadata.create_all(engine)


# Mã hóa mật khẩu
ph = PasswordHasher()


class UserManager:
    def __init__(self):
        self.session = Session()

    def register(self, username, password, email):
        if self.session.query(User).filter_by(username=username).first() is not None:
            return "Tên đăng nhập đã tồn tại"

        hashed_password = ph.hash(password)
        new_user = User(username=username, hashed_password=hashed_password, email=email, created_at=datetime.utcnow())

        try:
            self.session.add(new_user)
            self.session.commit()
            return "Đăng ký thành công"
        except Exception as e:
            self.session.rollback()
            return f"Đã xảy ra lỗi: {str(e)}"

    def login(self, username, password):
        user = self.session.query(User).filter_by(username=username).first()
        if user is None:
            return "Tên đăng nhập không tồn tại"

        try:
            ph.verify(user.hashed_password, password)
            return f"Token: {self.create_jwt(username)}, Refresh Token: {self.create_refresh_token(username)}"
        except argon2_exceptions.VerifyMismatchError:
            return "Mật khẩu không đúng"

    def create_jwt(self, username):
        secret_key = os.getenv("SECRET_KEY")
        if secret_key is None:
            return "SECRET_KEY chưa được thiết lập trong biến môi trường"

        expiration_time = datetime.utcnow() + timedelta(hours=1)
        payload = {
            'username': username,
            'exp': expiration_time
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    def create_refresh_token(self, username):
        secret_key = os.getenv("SECRET_KEY")
        if secret_key is None:
            return "SECRET_KEY chưa được thiết lập trong biến môi trường"

        expiration_time = datetime.utcnow() + timedelta(days=7)
        payload = {
            'username': username,
            'exp': expiration_time
        }
        refresh_token = jwt.encode(payload, secret_key, algorithm='HS256')
        return refresh_token

    def logout(self, token):
        secret_key = os.getenv("SECRET_KEY")
        if secret_key is None:
            raise ValueError("SECRET_KEY chưa được thiết lập trong biến môi trường")

        jti = jwt.decode(token, secret_key, algorithms=['HS256'])['jti']
        blacklist_token(jti)  # Thêm token vào blacklist


# Lớp UserData để quản lý dữ liệu người dùng
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


# Lớp Register để kiểm tra và đăng ký người dùng
class Register:
    def __init__(self):
        self.session = Session()

    def register(self, username, password, email):
        if self.session.query(User).filter_by(username=username).first():
            return "Tên người dùng đã tồn tại"

        hashed_password = ph.hash(password)
        new_user = User(username=username, hashed_password=hashed_password, email=email)
        self.session.add(new_user)
        self.session.commit()
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

    def is_username_valid(self, username):
        if len(username) < 3:
            return False
        if not username.isalnum():
            return False
        return True


# Lớp LoginWindow để tạo giao diện đăng nhập
class LoginWindow(QWidget):
    auth_result_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.auth_result_signal.connect(self.handle_auth_result)

    def initUI(self):
        self.setWindowTitle('Đăng nhập')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        title = QLabel('Đăng nhập vào hệ thống', self)
        layout.addWidget(title)

        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText("Tên người dùng")
        layout.addWidget(self.username_entry)

        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Mật khẩu")
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        login_button = QPushButton('Đăng nhập', self)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        register_button = QPushButton('Đăng ký', self)
        register_button.clicked.connect(self.register)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        user_manager = UserManager()

        threading.Thread(target=self.authenticate_login, args=(user_manager, username, password)).start()

    def authenticate_login(self, user_manager, username, password):
        response = user_manager.login(username, password)
        self.auth_result_signal.emit(response)

    def register(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        email = "email@example.com"  # Thay đổi để lấy email từ một trường nhập liệu nếu cần
        user_manager = UserManager()

        threading.Thread(target=self.authenticate_register, args=(user_manager, username, password, email)).start()

    def authenticate_register(self, user_manager, username, password, email):
        response = user_manager.register(username, password, email)
        self.auth_result_signal.emit(response)

    def handle_auth_result(self, response):
        if "Token:" in response:
            QMessageBox.information(self, 'Đăng nhập thành công', 'Đăng nhập thành công')
            self.open_main_app()
        else:
            QMessageBox.critical(self, 'Thất bại', response)

    def open_main_app(self):
        # Chúng ta sẽ không nhập MainApp ở đây
        from app.main import MainApp  # Import tại đây để tránh vòng lặp
        self.main_app = MainApp()
        self.main_app.show()
        self.close()


if __name__ == "__main__":
    app = QApplication([])
    window = LoginWindow()
    window.show()
    app.exec_()
