import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher
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
