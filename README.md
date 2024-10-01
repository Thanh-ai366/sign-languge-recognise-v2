# Sign Language Recognition

## Giới thiệu
Phần mềm nhận diện ngôn ngữ ký hiệu sử dụng mô hình học sâu (CNN) để phân tích các ký hiệu từ webcam. Phần mềm hỗ trợ dịch các ký hiệu sang văn bản, phát âm giọng nói, cung cấp phản hồi trực quan và theo dõi tiến độ học tập của người dùng.

## Chức năng chính
- **Nhận diện ký hiệu**: Nhận diện các ký hiệu ngôn ngữ từ webcam và dịch chúng sang văn bản.
- **Phát âm ký hiệu (Text-to-Speech - TTS)**: Chuyển đổi văn bản ký hiệu thành giọng nói với các tùy chọn tùy chỉnh tốc độ và ngôn ngữ phát âm.
- **Học tập thông minh**: Hệ thống học tập cung cấp các bài học và phản hồi trực quan về độ chính xác của ký hiệu.
- **Theo dõi tiến độ**: Ghi lại và phân tích tiến độ học tập của người dùng, bao gồm độ chính xác, thời gian thực hiện, và số lần thực hành.
- **Phân tích nâng cao**: Phân tích xu hướng tiến độ theo thời gian và hiển thị kết quả qua biểu đồ.

## Cài đặt

### Yêu cầu hệ thống
- **Python 3.6+**
- **TensorFlow/Keras**
- **Các thư viện khác** (liệt kê trong `requirements.txt`)

### Hướng dẫn cài đặt

1. **Clone dự án từ GitHub**:
   ```bash
   git clone https://github.com/Thanh-ai366/sign-language-recognise.git
   cd sign-language-recognise
