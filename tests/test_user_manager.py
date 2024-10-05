class TestUserManager:
    def setup_method(self):
        self.user_manager = UserManager()
        self.test_username = "testuser"
        self.test_password = "TestPass123!"
        self.test_email = "test@example.com"

    def test_register_success(self):
        result = self.user_manager.register(self.test_username, self.test_password, self.test_email)
        assert result == "Đăng ký thành công"

    def test_register_duplicate_username(self):
        self.user_manager.register(self.test_username, self.test_password, self.test_email)
        result = self.user_manager.register(self.test_username, "AnotherPass456!", "another@example.com")
        assert result == "Tên đăng nhập đã tồn tại"

    def test_login_success(self):
        self.user_manager.register(self.test_username, self.test_password, self.test_email)
        result = self.user_manager.login(self.test_username, self.test_password)
        assert "Token:" in result
        assert "Refresh Token:" in result

    def test_login_wrong_password(self):
        self.user_manager.register(self.test_username, self.test_password, self.test_email)
        result = self.user_manager.login(self.test_username, "WrongPass123!")
        assert result == "Mật khẩu không đúng"

    def test_login_nonexistent_user(self):
        result = self.user_manager.login("nonexistentuser", "SomePass123!")
        assert result == "Tên đăng nhập không tồn tại"

    def test_create_jwt(self):
        token = self.user_manager.create_jwt(self.test_username)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        refresh_token = self.user_manager.create_refresh_token(self.test_username)
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0

    def test_logout(self, mocker):
        mock_blacklist_token = mocker.patch('app.user_manager.blacklist_token')
        mock_jwt_decode = mocker.patch('jwt.decode', return_value={'jti': 'test_jti'})
        
        self.user_manager.logout("fake_token")
        
        mock_jwt_decode.assert_called_once()
        mock_blacklist_token.assert_called_once_with('test_jti')

class TestUserData:
    def setup_method(self):
        from app.user_manager import UserData
        self.test_username = "testuser"
        self.user_data = UserData(self.test_username, data_file="test_user_data.json")

    def test_load_user_data_nonexistent_file(self):
        assert self.user_data.data == {}

    def test_update_and_save_user_data(self, tmpdir):
        from app.user_manager import UserData
        self.user_data.data_file = tmpdir.join("test_user_data.json")
        self.user_data.update_data("key1", "value1")
        
        loaded_data = UserData(self.test_username, data_file=str(self.user_data.data_file)).data
        assert loaded_data == {"key1": "value1"}

    def test_update_existing_data(self, tmpdir):
        self.user_data.data_file = tmpdir.join("test_user_data.json")
        self.user_data.update_data("key1", "value1")
        self.user_data.update_data("key1", "new_value")
        
        loaded_data = UserData(self.test_username, data_file=str(self.user_data.data_file)).data
        assert loaded_data == {"key1": "new_value"}

class TestRegister:
    def setup_method(self):
        from app.user_manager import Register
        self.register = Register()

    def test_is_password_valid_success(self):
        assert self.register.is_password_valid("ValidPass123!")

    def test_is_password_valid_too_short(self):
        assert not self.register.is_password_valid("Short1!")

    def test_is_password_valid_no_digit(self):
        assert not self.register.is_password_valid("NoDigitPass!")

    def test_is_password_valid_no_letter(self):
        assert not self.register.is_password_valid("12345678!")

    def test_is_password_valid_no_special_char(self):
        assert not self.register.is_password_valid("NoSpecialChar123")

    def test_is_username_valid_success(self):
        assert self.register.is_username_valid("validuser123")

    def test_is_username_valid_too_short(self):
        assert not self.register.is_username_valid("ab")

    def test_is_username_valid_non_alphanumeric(self):
        assert not self.register.is_username_valid("user@name")

class TestLoginWindow:
    def test_login_window_init(self, qtbot):
        window = LoginWindow()
        qtbot.addWidget(window)

        assert window.windowTitle() == 'Đăng nhập'
        assert window.username_entry.placeholderText() == "Tên người dùng"
        assert window.password_entry.placeholderText() == "Mật khẩu"
        assert window.password_entry.echoMode() == QLineEdit.Password

    def test_login_success(self, qtbot, mocker):
        window = LoginWindow()
        qtbot.addWidget(window)

        mocker.patch.object(UserManager, 'login', return_value="Token: fake_token, Refresh Token: fake_refresh_token")
        mock_open_main_app = mocker.patch.object(window, 'open_main_app')

        qtbot.keyClicks(window.username_entry, "testuser")
        qtbot.keyClicks(window.password_entry, "testpass")
        qtbot.mouseClick(window.findChild(QPushButton, 'Đăng nhập'), Qt.LeftButton)

        qtbot.waitUntil(lambda: mock_open_main_app.called)
        mock_open_main_app.assert_called_once()

    def test_login_failure(self, qtbot, mocker):
        window = LoginWindow()
        qtbot.addWidget(window)

        mocker.patch.object(UserManager, 'login', return_value="Mật khẩu không đúng")
        mock_qmessagebox = mocker.patch('PyQt5.QtWidgets.QMessageBox.critical')

        qtbot.keyClicks(window.username_entry, "testuser")
        qtbot.keyClicks(window.password_entry, "wrongpass")
        qtbot.mouseClick(window.findChild(QPushButton, 'Đăng nhập'), Qt.LeftButton)

        qtbot.waitUntil(lambda: mock_qmessagebox.called)
        mock_qmessagebox.assert_called_once_with(window, 'Thất bại', "Mật khẩu không đúng")

    def test_register_success(self, qtbot, mocker):
        from login_window import LoginWindow
        window = LoginWindow()
        qtbot.addWidget(window)

        mocker.patch.object(UserManager, 'register', return_value="Đăng ký thành công")
        mock_qmessagebox = mocker.patch('PyQt5.QtWidgets.QMessageBox.information')

        qtbot.keyClicks(window.username_entry, "newuser")
        qtbot.keyClicks(window.password_entry, "newpass123")
        qtbot.mouseClick(window.findChild(QPushButton, 'Đăng ký'), Qt.LeftButton)

        qtbot.waitUntil(lambda: mock_qmessagebox.called)
        mock_qmessagebox.assert_called_once_with(window, 'Đăng ký thành công', "Đăng ký thành công")

    def test_register_failure(self, qtbot, mocker):
        window = LoginWindow()
        qtbot.addWidget(window)

        mocker.patch.object(UserManager, 'register', return_value="Tên đăng nhập đã tồn tại")
        mock_qmessagebox = mocker.patch('PyQt5.QtWidgets.QMessageBox.critical')

        qtbot.keyClicks(window.username_entry, "existinguser")
        qtbot.keyClicks(window.password_entry, "somepass123")
        qtbot.mouseClick(window.findChild(QPushButton, 'Đăng ký'), Qt.LeftButton)

        qtbot.waitUntil(lambda: mock_qmessagebox.called)
        mock_qmessagebox.assert_called_once_with(window, 'Thất bại', "Tên đăng nhập đã tồn tại")
