import os
import threading
import jwt
import secrets
import datetime
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QApplication, QMainWindow
)
from PyQt5.QtCore import pyqtSignal, QTimer
from sqlalchemy import create_engine, Column, String, DateTime, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from argon2 import PasswordHasher, exceptions as argon2_exceptions
from user_manager import LoginWindow, UserManager
import redis
import uuid

if "SECRET_KEY" not in os.environ:
    os.environ["SECRET_KEY"] = secrets.token_hex(32)  # Tạo một secret key ngẫu nhiên
    print("Đã tạo secret key:", os.environ["SECRET_KEY"])
else:
    print("Secret key đã được thiết lập.")
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("Kết nối Redis thành công")
except redis.ConnectionError as e:
    print(f"Lỗi kết nối Redis: {e}")

def add_blacklisted_tokens_column():
    inspector = inspect(engine)
    if 'users' in inspector.get_table_names():
        columns = [column['name'] for column in inspector.get_columns('users')]
        if 'blacklisted_tokens' not in columns:
            # Thêm cột blacklisted_tokens nếu chưa tồn tại
            with engine.connect() as connection:
                connection.execute('ALTER TABLE users ADD COLUMN blacklisted_tokens TEXT DEFAULT "";')
            print("Đã thêm cột blacklisted_tokens vào bảng users.")


def blacklist_token(jti):
    r.set(jti, 'blacklisted', ex=timedelta(hours=1))


def is_token_blacklisted(jti):
    return r.get(jti) is not None

def add_padding(token):
    """Thêm padding vào token để đảm bảo chuỗi Base64 hợp lệ."""
    missing_padding = len(token) % 4
    if missing_padding:
        token += '=' * (4 - missing_padding)
    return token

# Cấu hình SQLAlchemy
Base = declarative_base()
engine = create_engine('sqlite:///data/users.db')
Session = sessionmaker(bind=engine)

class MainApp(QMainWindow):
    def __init__(self, token, refresh_token):
        super().__init__()
        self.token = token
        self.refresh_token = refresh_token
        self.setWindowTitle("Ứng dụng chính")
        self.setGeometry(200, 200, 800, 600)

        # Giao diện chính
        layout = QVBoxLayout()
        try:
            username = self.get_username_from_token()
            label = QLabel(f"Chào mừng bạn {username}!", self)
        except ValueError as e:
            QMessageBox.critical(self, 'Lỗi Token', str(e))
            self.refresh_jwt_token()

        layout.addWidget(label)

        # Tạo các nút bấm trong giao diện
        self.create_buttons(layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def get_username_from_token(self):
        """Lấy tên người dùng từ token"""
        user_manager = UserManager()
        user = user_manager.get_user_from_token(self.token)
        return user.username if user else "Người dùng không xác định"

    def refresh_jwt_token(self):
        """Làm mới JWT token khi hết hạn"""
        user_manager = UserManager()
        new_token = user_manager.refresh_jwt(self.refresh_token)
        if new_token:
            self.token = new_token  # Cập nhật token mới
            QMessageBox.information(self, 'Token mới', 'Đã làm mới token của bạn.')
        else:
            QMessageBox.critical(self, 'Lỗi', 'Không thể làm mới token, vui lòng đăng nhập lại.')
            self.close()



class User(Base):
    def __init__(self, username):
        self.username = username

    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    hashed_password = Column(String)
    created_at = Column(DateTime)
    blacklisted_tokens = Column(String)

# Khởi tạo bảng trong database nếu chưa tồn tại
Base.metadata.create_all(engine)

# Mã hóa mật khẩu
ph = PasswordHasher()

# Lớp UserData để quản lý dữ liệu người dùng
class UserManager:
    def __init__(self):
        self.session = Session()

    def register(self, username, password):
        if self.session.query(User).filter_by(username=username).first() is not None:
            return "Tên đăng nhập đã tồn tại"

        hashed_password = ph.hash(password)
        new_user = User(username=username, hashed_password=hashed_password, created_at=datetime.utcnow())
        
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
            return {
                "token": self.create_jwt(username),
                "refresh_token": self.create_refresh_token(username),
            }
        except argon2_exceptions.VerifyMismatchError:
            return "Mật khẩu không đúng"

    def create_jwt(self, username):
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            raise ValueError("SECRET_KEY chưa được thiết lập trong biến môi trường")

        expiration_time = datetime.utcnow() + timedelta(hours=1)
        jti = str(uuid.uuid4())  # Tạo JTI (JWT ID) duy nhất
        payload = {
            'username': username,
            'exp': expiration_time,
            'jti': jti
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    def blacklist_token(self, jti, username):
        user = self.session.query(User).filter_by(username=username).first()
        if user.blacklisted_tokens:
            user.blacklisted_tokens += f",{jti}"
        else:
            user.blacklisted_tokens = jti
        self.session.commit()

    def is_token_blacklisted(self, jti, username):
        user = self.session.query(User).filter_by(username=username).first()
        if user and user.blacklisted_tokens:
            return jti in user.blacklisted_tokens.split(',')
        return False
    
    def refresh_jwt(self, refresh_token):
        try:
            decoded_token = jwt.decode(refresh_token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
            username = decoded_token['username']
            return self.create_jwt(username)  # Tạo JWT mới từ username
        except jwt.ExpiredSignatureError:
            return None  # Refresh token cũng hết hạn, yêu cầu đăng nhập lại
        except jwt.InvalidTokenError:
            return None  # Refresh token không hợp lệ

    def create_refresh_token(self, username):
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            return "Lỗi: SECRET_KEY chưa được thiết lập trong biến môi trường"

        expiration_time = datetime.utcnow() + timedelta(days=7)
        payload = {
            'username': username,
            'exp': expiration_time
        }
        refresh_token = jwt.encode(payload, secret_key, algorithm='HS256')
        return refresh_token

    def get_user_from_token(self, token):
        try:
            # Thêm padding vào token nếu thiếu
            token = add_padding(token)
            decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
            username = decoded_token.get('username')
            if username:
                return self.session.query(User).filter_by(username=username).first()
            else:
                raise ValueError("Token không chứa thông tin username.")
        except jwt.ExpiredSignatureError:
            raise ValueError("Token đã hết hạn.")
        except jwt.InvalidTokenError:
            raise ValueError("Token không hợp lệ.")

    def logout(self, token):
        jti = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])['jti']
        blacklist_token(jti)  # Thêm token vào blacklist

class LoginWindow(QWidget):
    auth_result_signal = pyqtSignal(object)

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

        # Nút mở cửa sổ đăng ký
        register_button = QPushButton('Đăng ký', self)
        register_button.clicked.connect(self.open_register_window)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def open_register_window(self):
        register_window = RegisterWindow()
        register_window.show()

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        user_manager = UserManager()
        result = user_manager.login(username, password)
        self.auth_result_signal.emit(result)

    def handle_auth_result(self, response):
        if isinstance(response, dict):  # Nếu phản hồi là từ điển
            token = response["token"]
            refresh_token = response["refresh_token"]
            QMessageBox.information(self, 'Đăng nhập thành công', 'Đăng nhập thành công')
            self.open_main_app(token, refresh_token)  # Gọi hàm với 2 đối số
        else:
            QMessageBox.critical(self, 'Thất bại', response)

    def open_main_app(self, token, refresh_token):
        main_app = MainApp(token, refresh_token)
        main_app.show()
        self.close()  # Đóng cửa sổ đăng nhập

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Đăng ký')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        title = QLabel('Đăng ký tài khoản', self)
        layout.addWidget(title)

        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText("Tên người dùng")
        layout.addWidget(self.username_entry)

        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Mật khẩu")
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        register_button = QPushButton('Đăng ký', self)
        register_button.clicked.connect(self.register)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def register(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        user_manager = UserManager()
        result = user_manager.register(username, password)
        QMessageBox.information(self, 'Kết quả', result)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
