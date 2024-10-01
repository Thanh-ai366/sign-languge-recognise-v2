import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from train_cnn_model import train_model  # Hàm huấn luyện mô hình

class NewDataHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        print(f"Đã phát hiện dữ liệu mới: {event.src_path}")
        train_model()

def monitor_data_folder(folder_path):
    event_handler = NewDataHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()
    print(f"Đang giám sát thư mục {folder_path}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    folder_to_monitor = "./data/new_data"
    monitor_data_folder(folder_to_monitor)
