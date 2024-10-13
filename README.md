# Hệ thống nhận diện ngôn ngữ ký hiệu

## Giới thiệu
Hệ thống nhận diện ngôn ngữ ký hiệu sử dụng mô hình học sâu (CNN) để phân tích và dự đoán các ký hiệu tay dựa trên hình ảnh từ camera. Dự án này nhằm hỗ trợ người khuyết tật trong việc giao tiếp và học ngôn ngữ ký hiệu, giúp nâng cao khả năng giao tiếp cho cộng đồng.

Dự án bao gồm các chức năng chính như:
- **Dự đoán ký hiệu tay** từ hình ảnh camera.
- **Học ngôn ngữ ký hiệu** thông qua các bài học và hướng dẫn.
- **Phân tích dữ liệu** từ quá trình học tập và dự đoán.

## Cấu trúc dự án
```
sign-language-recognise/
│
├── app/
│     ├── images/  ( Chứa hình ảnh cho learning.py)
│     ├── data/
│            ├── processed/            # Dữ liệu đã qua xử lý
│            └── saved_models/         # Mô hình đã huấn luyện
│                       ├── cnn_model_best.keras
│            └── logs/
│                       ├── sign_usage.csv
│            └── users.json 
│     ├── templates/
│            ├── dashboard.html/
│     ├── models/
│            ├── __init__.py
│            ├── cnn_model.py          # Mô hình CNN
│            ├── __pycache__/
│            └── model_loader.py       # Tải và lưu trữ các mô hình            
│     ├── __init__.py
│     ├── api.py         
│     ├── dashboard.py       
│     ├── main.py                 # Giao diện chính của phần mềm
│     ├── train_cnn_model   # Huấn luyện mô hình từ dữ liệu có sẵn
│     ├── prediction.py         # Module dự đoán ngôn ngữ ký hiệu
│     ├── dataset_manager.py    # Quản lý và xử lý dataset
│     ├── __pycache__/
│     ├── analytics.py
│     ├── user_manager.py
│     ├── learning.py
│     ├── sign_predictions.txt
│     └── utils.py              # Các hàm tiện ích chung
│
├── gui/
│   ├── assets/               # Hình ảnh icon và tài nguyên giao diện
│   └── styles.py             # Phong cách giao diện (màu sắc font...)
│
├── tests/
│   ├── test_models.py        # Kiểm tra mô hình
│   ├── test_prediction.py    # Kiểm tra chức năng dự đoán
│   └── test_gui.py           # Kiểm tra giao diện người dùng
│
├── config/
│   ├── logstash.conf
│
├── logs/
│   ├── api_requests.log
│
├── temp/
│
├── .gitlab-ci.yml/
│
├── deployment.yaml/
│
├── Dockerfile.txt/
│
├── backup&restore.sh/
│
├── train_model_auto.py/
│
├── README.md                 # Hướng dẫn sử dụng và cài đặt
├── requirements.txt          # Các thư viện cần thiết
└── setup.py                  # Cấu hình cài đặt dự án
```

## Yêu cầu hệ thống
- Python 3.8+
- Các thư viện Python cần thiết (xem trong `requirements.txt`):
  - TensorFlow
  - OpenCV
  - PyQt5
  - Flask
  - NumPy, Matplotlib, 
  - etc...

## Cài đặt
1. **Clone repository:**
   ```
   git clone https://github.com/username/sign-language-recognise.git
   cd sign-language-recognise
   ```

2. **Cài đặt các thư viện cần thiết:**
   ```
   pip install -r requirements.txt
   ```

3. **Cấu hình hệ thống:**
   - Đảm bảo có thư mục `app/data/saved_models/` và đặt mô hình huấn luyện sẵn `cnn_model_best.keras` tại đó.

## Sử dụng
### 1. Chạy ứng dụng
Khởi động giao diện chính của phần mềm với PyQt:

python app/main.py

Giao diện chính sẽ mở ra với các chức năng: 
- **Dự đoán ngôn ngữ ký hiệu**
- **Học ngôn ngữ ký hiệu**
- **Phân tích dữ liệu**

### 2. Huấn luyện mô hình
Nếu muốn huấn luyện lại mô hình với dữ liệu của riêng bạn:
```
python train_cnn_model.py
```

### 3. API Dự đoán
Khởi động server Flask để sử dụng API dự đoán:

python app/api.py

Sử dụng lệnh sau để gửi yêu cầu dự đoán với ảnh:

curl -X POST http://127.0.0.1:5000/predict -F 'image=@path_to_image.jpg' -H "Authorization: Bearer <token>"


## Các tính năng chính
1. **Dự đoán ngôn ngữ ký hiệu:**
   - Mô hình CNN dự đoán ký hiệu tay từ hình ảnh.
   - Kết quả được hiển thị trực tiếp trên giao diện người dùng và có khả năng tương tác bằng giọng nói.

2. **Học ngôn ngữ ký hiệu:**
   - Các bài học về ngôn ngữ ký hiệu, kèm theo hướng dẫn bằng hình ảnh và kiểm tra tiến trình học của người dùng.
   
3. **Phân tích dữ liệu:**
   - Dashboard trực quan giúp phân tích dữ liệu dự đoán, hiển thị biểu đồ SSIM (Structural Similarity Index Measure), độ chính xác của dự đoán và thời gian phản hồi.

## Kiểm thử
Thư mục `tests/` chứa các tệp kiểm thử cho từng module:
- Kiểm thử mô hình: `test_models.py`
- Kiểm thử dự đoán: `test_prediction.py`
- Kiểm thử giao diện: `test_gui.py`
- ....

Chạy các kiểm thử:
```
pytest tests/
```

## Cải thiện và mở rộng
- **Thêm dữ liệu mới:** Bạn có thể mở rộng dataset bằng cách thêm các ký hiệu mới vào thư mục dữ liệu và huấn luyện lại mô hình.
- **Nâng cao mô hình:** Tối ưu mô hình bằng cách thử nghiệm với các kiến trúc mạng khác nhau như ResNet, EfficientNet.

## Đóng góp
Chúng tôi hoan nghênh các đóng góp cho dự án. Nếu bạn phát hiện lỗi hoặc có ý tưởng mới, hãy tạo issue hoặc gửi pull request.

## Giấy phép
Dự án này được cấp phép theo [MIT License](LICENSE).

