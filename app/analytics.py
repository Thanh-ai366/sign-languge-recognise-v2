# analytics.py
import csv
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
        self.headers = ["Timestamp", "Sign", "Accuracy", "Time Taken"]

        directory = os.path.dirname(self.file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Tạo tệp và ghi header nếu tệp chưa tồn tại
        if not self._file_exists():
            with open(self.file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)

    def _file_exists(self):
        return os.path.exists(self.file_path)

    def log(self, sign, accuracy, time_taken):
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, sign, accuracy, time_taken])
        except Exception as e:
            print(f"Lỗi khi ghi dữ liệu: {e}")

class SignAnalysis:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

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
                        data[sign].append((accuracy, time_taken))
                    except ValueError as e:
                        print(f"Lỗi trong dữ liệu: {e}")
                        continue
        except FileNotFoundError:
            print(f"Tệp {self.file_path} không tồn tại!")
        return data

    def generate_report(self):
        report_data = []
        for sign, entries in self.data.items():
            avg_accuracy = np.mean([acc for acc, _ in entries])
            avg_time = np.mean([time for _, time in entries])
            report_data.append((sign, avg_accuracy, avg_time))
            print(f"Ký hiệu: {sign} - Độ chính xác trung bình: {avg_accuracy:.2f} - Thời gian trung bình: {avg_time:.2f} giây")
        return report_data

    def plot_accuracy(self):
        signs = []
        accuracies = []
        for sign, entries in self.data.items():
            avg_accuracy = np.mean([acc for acc, _ in entries])
            signs.append(sign)
            accuracies.append(avg_accuracy)

        plt.figure(figsize=(10, 5))
        plt.bar(signs, accuracies, color='blue')
        plt.xlabel('Ký hiệu')
        plt.ylabel('Độ chính xác trung bình')
        plt.title('Độ chính xác trung bình của các ký hiệu')
        plt.show()

    def plot_time(self):
        signs = []
        times = []
        for sign, entries in self.data.items():
            avg_time = np.mean([time for _, time in entries])
            signs.append(sign)
            times.append(avg_time)

        plt.figure(figsize=(10, 5))
        plt.bar(signs, times, color='green')
        plt.xlabel('Ký hiệu')
        plt.ylabel('Thời gian trung bình (giây)')
        plt.title('Thời gian trung bình cho các ký hiệu')
        plt.show()

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
        for sign, avg_accuracy, avg_time in report_data:
            self.add_section(f"Ký hiệu: {sign}", 
                             f"Độ chính xác trung bình: {avg_accuracy:.2f}\nThời gian trung bình: {avg_time:.2f} giây")
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

class LogDataWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Log Data")

        self.logger = DataLogger("data/logs/sign_usage.csv")

        # Nhập ký hiệu
        self.sign_input = QLineEdit(self)
        self.sign_input.setPlaceholderText("Nhập ký hiệu")

        # Nhập độ chính xác
        self.accuracy_input = QLineEdit(self)
        self.accuracy_input.setPlaceholderText("Nhập độ chính xác (0-1)")

        # Nhập thời gian
        self.time_input = QLineEdit(self)
        self.time_input.setPlaceholderText("Nhập thời gian (giây)")

        # Nút Log
        self.log_button = QPushButton("Log")
        self.log_button.clicked.connect(self.log_data)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ký hiệu"))
        layout.addWidget(self.sign_input)
        layout.addWidget(QLabel("Độ chính xác"))
        layout.addWidget(self.accuracy_input)
        layout.addWidget(QLabel("Thời gian"))
        layout.addWidget(self.time_input)
        layout.addWidget(self.log_button)

        self.setLayout(layout)

    def log_data(self):
        sign = self.sign_input.text()
        accuracy = float(self.accuracy_input.text())
        time_taken = float(self.time_input.text())

        self.logger.log(sign, accuracy, time_taken)
        self.accept()

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

        layout = QVBoxLayout()
        layout.addWidget(self.report_button)
        layout.addWidget(self.plot_accuracy_button)
        layout.addWidget(self.plot_time_button)
        layout.addWidget(self.report_pdf_button)

        self.setLayout(layout)

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

        # Nút mở cửa sổ Log Data
        self.log_data_button = QPushButton("Log Data")
        self.log_data_button.clicked.connect(self.open_log_data_window)

        # Nút mở cửa sổ phân tích
        self.analysis_button = QPushButton("Xem phân tích")
        self.analysis_button.clicked.connect(self.open_analysis_window)

        # Tạo layout
        layout = QVBoxLayout()
        layout.addWidget(self.log_data_button)
        layout.addWidget(self.analysis_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_log_data_window(self):
        self.log_data_window = LogDataWindow()
        self.log_data_window.show()

    def open_analysis_window(self):
        self.analysis_window = AnalysisWindow()
        self.analysis_window.show()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
