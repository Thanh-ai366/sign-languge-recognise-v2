import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.api import app, predict_api, login_api, register_api, logout_api
import jwt
import json

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.api.register_user')
    def test_register_api(self, mock_register_user):
        mock_register_user.return_value = "User registered successfully"
        response = self.app.post('/register', json={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "User registered successfully")

    @patch('app.api.login')
    def test_login_api_success(self, mock_login):
        mock_login.return_value = "Token: fake_token"
        response = self.app.post('/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Đăng nhập thành công")
        self.assertEqual(data['token'], "fake_token")

    @patch('app.api.login')
    def test_login_api_failure(self, mock_login):
        mock_login.return_value = "Invalid credentials"
        response = self.app.post('/login', json={
            'username': 'testuser',
            'password': 'wrongpass'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Invalid credentials")

    @patch('app.api.jwt.decode')
    @patch('app.api.blacklist_token')
    def test_logout_api_success(self, mock_blacklist_token, mock_jwt_decode):
        mock_jwt_decode.return_value = {'jti': 'fake_jti'}
        response = self.app.post('/logout', headers={'Authorization': 'Bearer fake_token'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Đăng xuất thành công")
        mock_blacklist_token.assert_called_once_with('fake_jti')

    def test_logout_api_no_token(self):
        response = self.app.post('/logout')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['error'], "Token không được cung cấp")

    @patch('app.api.verify_token')
    @patch('app.api.SignLanguagePredictor')
    def test_predict_api_success(self, mock_predictor, mock_verify_token):
        mock_verify_token.return_value = True
        mock_predictor_instance = MagicMock()
        mock_predictor_instance.predict_with_cache.return_value = 'A'
        mock_predictor.return_value = mock_predictor_instance

        with patch('app.api.request.files') as mock_files:
            mock_image = MagicMock()
            mock_image.filename = 'test.jpg'
            mock_files.__getitem__.return_value = mock_image
            response = self.app.post('/predict', headers={'Authorization': 'Bearer fake_token'})

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['predicted_sign'], 'A')

    def test_predict_api_no_token(self):
        response = self.app.post('/predict')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['error'], "Token không được cung cấp")

    @patch('app.api.verify_token')
    def test_predict_api_invalid_token(self, mock_verify_token):
        mock_verify_token.return_value = False
        response = self.app.post('/predict', headers={'Authorization': 'Bearer fake_token'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['error'], "Token không hợp lệ hoặc đã hết hạn")

if __name__ == '__main__':
    unittest.main()

