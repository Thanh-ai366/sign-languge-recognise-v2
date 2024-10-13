import os
import time
import logging
import jwt
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from app.prediction import SignLanguagePredictor
from auth.login import login, register_user, verify_token
from auth.token import blacklist_token
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://<Your-Sentry-DSN-Here>",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename='logs/api_requests.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model_path = "app/data/saved_models/cnn_model_best.keras"
labels_dict = {i: str(i) for i in range(10)}
labels_dict.update({10 + i: chr(97 + i) for i in range(26)})

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/register', methods=['POST'])
def register_api():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    result = register_user(username, password, email)

    logging.info(f"Đăng ký: {username}, Email: {email}")

    return jsonify({'message': result})

@app.route('/login', methods=['POST'])
def login_api():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    result = login(username, password)

    logging.info(f"Đăng nhập: {username}")

    if "Token:" in result:
        return jsonify({'message': 'Đăng nhập thành công', 'token': result.split(": ")[1]})
    
    return jsonify({'message': result})

@app.route('/logout', methods=['POST'])
def logout_api():
    token = request.headers.get('Authorization')

    if token:
        try:
            decoded_token = jwt.decode(token.split(" ")[1], app.config['SECRET_KEY'], algorithms=["HS256"])
            blacklist_token(decoded_token['jti'])
            return jsonify({'message': 'Đăng xuất thành công'})
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token đã hết hạn'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token không hợp lệ'}), 401
    
    return jsonify({'error': 'Token không được cung cấp'}), 403

@app.route('/predict', methods=['POST'])
def predict_api():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'error': 'Token không được cung cấp'}), 403

    user = verify_token(token)

    if not user:
        return jsonify({'error': 'Token không hợp lệ hoặc đã hết hạn'}), 403

    if 'image' not in request.files:
        return jsonify({'message': 'Không tìm thấy tệp hình ảnh'}), 400

    image = request.files['image']
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    start_time = time.time()
    
    predictor = SignLanguagePredictor(model_path, labels_dict)
    try:
        predicted_sign = predictor.predict_with_cache(image_path)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return jsonify({'error': 'Đã xảy ra lỗi trong quá trình xử lý'}), 500

    end_time = time.time()
    response_time = end_time - start_time
    
    logging.info(f"Ảnh: {filename}, Kết quả: {predicted_sign}, Thời gian phản hồi: {response_time:.2f}s")

    os.remove(image_path)

    return jsonify({'predicted_sign': predicted_sign})

if __name__ == '__main__':
    app.run(debug=True)
