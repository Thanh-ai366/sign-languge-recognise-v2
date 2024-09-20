import json
from datetime import datetime

class ProgressTracker:
    def __init__(self, username, progress_file="learning/progress_data.json"):
        self.username = username
        self.progress_file = progress_file
        self.progress_data = self.load_progress_data()

    def load_progress_data(self):
        try:
            with open(self.progress_file, 'r') as file:
                all_progress = json.load(file)
                return all_progress.get(self.username, {})
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu tiến độ: {e}")
            return {}

    def save_progress_data(self):
        try:
            with open(self.progress_file, 'r') as file:
                all_progress = json.load(file)
        except FileNotFoundError:
            all_progress = {}
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu tiến độ: {e}")
            all_progress = {}

        all_progress[self.username] = self.progress_data

        try:
            with open(self.progress_file, 'w') as file:
                json.dump(all_progress, file)
            print("Dữ liệu tiến độ đã được lưu.")
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu tiến độ: {e}")

    def update_progress(self, lesson, accuracy):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        progress_entry = {
            'lesson': lesson,
            'accuracy': accuracy,
            'timestamp': timestamp
        }

        self.progress_data[timestamp] = progress_entry
        self.save_progress_data()

    def get_progress_report(self):
        report = [
            f"Buổi học: {entry['lesson']}, Độ chính xác: {entry['accuracy']}, Thời gian: {entry['timestamp']}"
            for entry in self.progress_data.values()
        ]
        return report
