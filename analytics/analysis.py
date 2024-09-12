import csv
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

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
                        sign = int(row["Sign"])  # Đảm bảo đọc nhãn dưới dạng số nguyên
                        accuracy = float(row["Accuracy"])
                        time_taken = float(row["Time Taken"])
                        data[sign].append((accuracy, time_taken))
                    except ValueError as e:
                        print(f"Lỗi trong dữ liệu: {e}")
                        continue  # Bỏ qua dòng lỗi
        except FileNotFoundError:
            print(f"Tệp {self.file_path} không tồn tại!")
        return data

    def generate_report(self):
        for sign, entries in self.data.items():
            avg_accuracy = np.mean([acc for acc, _ in entries])
            avg_time = np.mean([time for _, time in entries])
            print(f"Ký hiệu: {sign} - Độ chính xác trung bình: {avg_accuracy:.2f} - Thời gian trung bình: {avg_time:.2f} giây")

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

# Sử dụng SignAnalysis
if __name__ == "__main__":
    analyzer = SignAnalysis("data/logs/sign_usage.csv")
    analyzer.generate_report()
    analyzer.plot_accuracy()
