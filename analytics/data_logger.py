import csv
from datetime import datetime

class DataLogger:
    def __init__(self, file_path):
        self.file_path = file_path
        self.headers = ["Timestamp", "Sign", "Accuracy", "Time Taken"]

        # Tạo tệp và ghi header nếu tệp chưa tồn tại
        if not self._file_exists():
            with open(self.file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)

    def _file_exists(self):
        try:
            with open(self.file_path, mode='r'):
                return True
        except FileNotFoundError:
            return False

    def log(self, sign, accuracy, time_taken):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, sign, accuracy, time_taken])

# Sử dụng DataLogger
if __name__ == "__main__":
    logger = DataLogger("data/logs/sign_usage.csv")
    logger.log("A", 0.95, 1.5)
