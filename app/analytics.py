# analytics.py
import csv
import cv2
import os
from collections import defaultdict
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QLineEdit, QLabel, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class DataLogger:
    def __init__(self, file_path):
        self.file_path = file_path
        self.headers = ["Timestamp", "Sign", "Accuracy", "Time Taken", "Image Path"]
        if not os.path.exists(os.path.dirname(self.file_path)):
            os.makedirs(os.path.dirname(self.file_path))
        if not self._file_exists():
            with open(self.file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)


    def log(self, sign, accuracy, time_taken, image_path):
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, sign, accuracy, time_taken, image_path])
        except Exception as e:
            print(f"Lỗi khi ghi dữ liệu: {e}")

    def _file_exists(self):
        return os.path.exists(self.file_path)

    def log(self, sign, accuracy, time_taken, image_path):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, sign, accuracy, time_taken, image_path])

class SignAnalysis:
    IMAGE_SIZE = (64, 64)
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

    def plot_similarity(self):
        signs, similarities = self.compute_similarity()
        
        # Vẽ biểu đồ SSIM
        plt.figure(figsize=(10, 5))
        plt.bar(signs, similarities, color='purple')
        plt.xlabel('Ký hiệu')
        plt.ylabel('Độ giống nhau SSIM')
        plt.title('Độ giống nhau SSIM của các ký hiệu')
        plt.show()

    def load_data(self):
        data = defaultdict(list)
        try:
            with open(self.file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        sign = int(row["Sign"])
                        accuracy = float(row["Accuracy"])
                        time_taken = float(row["Time Taken"])
                        image_path = row["Image Path"]  # Sửa tên trường CSV cho đúng
                        data[sign].append((accuracy, time_taken, image_path))
                    except ValueError as e:
                        print(f"Lỗi trong dữ liệu: {e}")
                        continue
        except FileNotFoundError:
            print(f"Tệp {self.file_path} không tồn tại!")
        return data

    def compare_images(self, img_path1, img_path2):
        if not os.path.exists(img_path1) or not os.path.exists(img_path2):
            print(f"Không tìm thấy một trong hai ảnh: {img_path1}, {img_path2}")
            return 0.0

        img1 = cv2.imread(img_path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(img_path2, cv2.IMREAD_GRAYSCALE)

        if img1 is None or img2 is None:
            print(f"Lỗi khi đọc ảnh: {img_path1}, {img_path2}")
            return 0.0

        img1 = cv2.resize(img1, self.IMAGE_SIZE)
        img2 = cv2.resize(img2, self.IMAGE_SIZE)

        from skimage.metrics import structural_similarity as ssim
        similarity_index, _ = ssim(img1, img2, full=True)

        return similarity_index

    def generate_report(self):
        report_data = []
        for sign, entries in self.data.items():
            avg_accuracy = np.mean([acc for acc, _, _ in entries])
            avg_time = np.mean([time for _, time, _ in entries])
            sample_image = f"sample_images/{sign}.jpg"

            # So sánh các ảnh đã lưu với ảnh mẫu
            similarities = []
            for _, _, img_path in entries:
                similarity = self.compare_images(img_path, sample_image)
                similarities.append(similarity)

            avg_similarity = np.mean(similarities)  # Độ giống nhau trung bình với ảnh mẫu

            report_data.append((sign, avg_accuracy, avg_time, avg_similarity))
            print(f"Ký hiệu: {sign} - Độ chính xác: {avg_accuracy:.2f} - Thời gian: {avg_time:.2f}s - SSIM: {avg_similarity:.2f}")

        return report_data

    def compute_similarity(self):
        signs = []
        similarities = []
        for sign, entries in self.data.items():
            sample_image = f"sample_images/{sign}.jpg"
            similarity_list = [self.compare_images(img_path, sample_image) for _, _, img_path in entries]
            avg_similarity = np.mean(similarity_list)
            signs.append(sign)
            similarities.append(avg_similarity)
        return signs, similarities

    def plot_accuracy(self):
        signs, accuracies = self.compute_accuracy()

        plt.figure(figsize=(10, 5))
        plt.bar(signs, accuracies, color='blue')
        plt.xlabel('Ký hiệu')
        plt.ylabel('Độ chính xác trung bình')
        plt.title('Độ chính xác trung bình của các ký hiệu')
        plt.show()

    def compute_accuracy(self):
        signs = []
        accuracies = []
        for sign, entries in self.data.items():
            avg_accuracy = np.mean([acc for acc, _ in entries])
            signs.append(sign)
            accuracies.append(avg_accuracy)
        return signs, accuracies

    def plot_time(self):
        signs, times = self.compute_time()

        plt.figure(figsize=(10, 5))
        plt.bar(signs, times, color='green')
        plt.xlabel('Ký hiệu')
        plt.ylabel('Thời gian trung bình (giây)')
        plt.title('Thời gian trung bình cho các ký hiệu')
        plt.show()

    def compute_time(self):
        signs = []
        times = []
        for sign, entries in self.data.items():
            avg_time = np.mean([time for _, time in entries])
            signs.append(sign)
            times.append(avg_time)
        return signs, times

class ReportGenerator:
    def __init__(self, report_title):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 12)
        self.report_title = report_title
        self.pdf.cell(200, 10, txt=report_title, ln=True, align="C")

    def add_section(self, section_title, content):
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.cell(0, 10, txt=section_title, ln=True)
        self.pdf.set_font("Arial", "", 12)
        self.pdf.multi_cell(0, 10, txt=content)

    def save_report(self, file_path):
        self.pdf.output(file_path)

    def generate_report(self, report_data):
        for sign, avg_accuracy, avg_time, avg_similarity in report_data:
            self.add_section(f"Ký hiệu: {sign}", 
                             f"Độ chính xác trung bình: {avg_accuracy:.2f}\n"
                             f"Thời gian trung bình: {avg_time:.2f} giây\n"
                             f"Độ giống nhau SSIM: {avg_similarity:.2f}")
        self.save_report(f"data/reports/{datetime.now().strftime('%Y-%m-%d')}_sign_language_report.pdf")

class RealTimeAnalyzer:
    def __init__(self, logger):
        self.logger = logger
        self.analysis = SignAnalysis(logger.file_path)

    def update_analysis(self):
        self.analysis.data = self.analysis.load_data()  # Tải lại dữ liệu mới
        self.analysis.generate_report()
        self.analysis.plot_accuracy()
        self.analysis.plot_time()

class AnalysisWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Phân tích dữ liệu")

        self.analysis = SignAnalysis("data/logs/sign_usage.csv")

        # Nút hiển thị báo cáo
        self.report_button = QPushButton("Hiển thị báo cáo")
        self.report_button.clicked.connect(self.show_report)

        # Nút vẽ biểu đồ độ chính xác
        self.plot_accuracy_button = QPushButton("Vẽ biểu đồ độ chính xác")
        self.plot_accuracy_button.clicked.connect(self.plot_accuracy)

        # Nút vẽ biểu đồ thời gian
        self.plot_time_button = QPushButton("Vẽ biểu đồ thời gian")
        self.plot_time_button.clicked.connect(self.plot_time)

        # Nút tạo báo cáo PDF
        self.report_pdf_button = QPushButton("Tạo báo cáo PDF")
        self.report_pdf_button.clicked.connect(self.generate_pdf_report)

        # Nút vẽ biểu đồ độ giống nhau SSIM
        self.plot_similarity_button = QPushButton("Vẽ biểu đồ SSIM")
        self.plot_similarity_button.clicked.connect(self.plot_similarity)

        layout = QVBoxLayout()
        layout.addWidget(self.report_button)
        layout.addWidget(self.plot_accuracy_button)
        layout.addWidget(self.plot_time_button)
        layout.addWidget(self.report_pdf_button)
        layout.addWidget(self.plot_similarity_button)  # Thêm nút vào layout

        self.setLayout(layout)

    def plot_similarity(self):
        self.analysis.plot_similarity() 

    def show_report(self):
        self.analysis.generate_report()

    def plot_accuracy(self):
        self.analysis.plot_accuracy()

    def plot_time(self):
        self.analysis.plot_time()

    def generate_pdf_report(self):
        report_data = self.analysis.generate_report()
        report_generator = ReportGenerator("Báo cáo Ngôn ngữ Ký hiệu")
        report_generator.generate_report(report_data)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ngôn ngữ Ký hiệu - Phân tích")

        # Nút mở cửa sổ phân tích
        self.analysis_button = QPushButton("Xem phân tích")
        self.analysis_button.clicked.connect(self.open_analysis_window)

        # Tạo layout
        layout = QVBoxLayout()
        layout.addWidget(self.analysis_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_analysis_window(self):
        self.analysis_window = AnalysisWindow()
        self.analysis_window.show()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
