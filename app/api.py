import os
import time
import logging
import jwt
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from app.prediction import SignLanguagePredictor
from auth.login import login, register_user, verify_token
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Cấu hình Sentry với Flask
sentry_sdk.init(
    dsn="https://<Your-Sentry-DSN-Here>",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

# Cấu hình logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename='logs/api_requests.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Đường dẫn lưu trữ hình ảnh tải lên
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Đường dẫn đến mô hình và từ điển nhãn
model_path = "app/data/saved_models/cnn_model.h5"
labels_dict = {i: str(i) for i in range(10)}
labels_dict.update({10 + i: chr(97 + i) for i in range(26)})

# Tạo thư mục lưu trữ nếu chưa tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# API đăng ký người dùng
@app.route('/register', methods=['POST'])
def register_api():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    result = register_user(username, password, email)

    # Ghi log thông tin đăng ký
    logging.info(f"Đăng ký: {username}, Email: {email}")

    return jsonify({'message': result})

# API đăng nhập người dùng
@app.route('/login', methods=['POST'])
def login_api():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    result = login(username, password)

    # Ghi log thông tin đăng nhập
    logging.info(f"Đăng nhập: {username}")

    if "Token:" in result:
        return jsonify({'message': 'Đăng nhập thành công', 'token': result.split(": ")[1]})
    
    return jsonify({'message': result})

# API dự đoán ký hiệu ngôn ngữ từ hình ảnh
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

    # Ghi thời gian bắt đầu dự đoán
    start_time = time.time()
    
    # Khởi tạo predictor và dự đoán
    predictor = SignLanguagePredictor(model_path, labels_dict)
    try:
        predicted_sign = predictor.predict_with_cache(image_path)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return jsonify({'error': 'Đã xảy ra lỗi trong quá trình xử lý'}), 500

    # Ghi thời gian kết thúc và tính thời gian phản hồi
    end_time = time.time()
    response_time = end_time - start_time
    
    # Ghi log kết quả dự đoán và thời gian phản hồi
    logging.info(f"Ảnh: {filename}, Kết quả: {predicted_sign}, Thời gian phản hồi: {response_time:.2f}s")

    # Xóa tệp hình ảnh sau khi dự đoán
    os.remove(image_path)

    return jsonify({'predicted_sign': predicted_sign})

if __name__ == '__main__':
    app.run(debug=True)
