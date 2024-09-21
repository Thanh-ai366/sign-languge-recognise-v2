import os
import threading
import jwt
import datetime
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher, exceptions as argon2_exceptions
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime

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
            return f"Token: {self.create_jwt(username)}"
        except argon2_exceptions.VerifyMismatchError:
            return "Mật khẩu không đúng"

    def create_jwt(self, username):
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        payload = {
            'username': username,
            'exp': expiration_time
        }
        token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm='HS256')
        return token

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
        self.main_app = MainApp()  # Thay thế bằng class MainApp của bạn
        self.main_app.show()
        self.close()
