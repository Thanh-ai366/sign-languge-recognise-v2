import json
import os

class ProgressTracker:
    def __init__(self, user_id, data_dir="data/progress/"):
        self.user_id = user_id
        self.data_dir = data_dir
        self.progress_file = os.path.join(data_dir, f"{user_id}_progress.json")
        self.progress = self.load_progress()

    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_progress(self):
        with open(self.progress_file, 'w') as file:
            json.dump(self.progress, file, indent=4)

    def update_progress(self, sign, accuracy, time_taken, repetitions, smoothness):
        if sign not in self.progress:
            self.progress[sign] = []
        self.progress[sign].append({
            "accuracy": accuracy,
            "time_taken": time_taken,
            "repetitions": repetitions,
            "smoothness": smoothness
        })
        self.save_progress()

    def get_progress(self):
        return self.progress

# Sử dụng ProgressTracker để theo dõi tiến bộ của người dùng
if __name__ == "__main__":
    tracker = ProgressTracker("user_01")
    tracker.update_progress("A", 0.95, 1.2, 10, 0.85)
    tracker.update_progress("B", 0.85, 1.5, 8, 0.90)
    print(tracker.get_progress())
