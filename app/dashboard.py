from flask import Flask, render_template
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# API phân tích hiệu suất và tạo biểu đồ
@app.route('/dashboard')
def dashboard():
    # Đọc dữ liệu từ file log
    response_times = []
    timestamps = []
   
    log_file_path = 'logs/api_requests.log'
   
    # Kiểm tra xem tệp log có tồn tại không
    if not os.path.exists(log_file_path):
        return "Log file not found.", 404

    try:
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                if 'Thời gian phản hồi' in line:
                    parts = line.split(' - ')
                    timestamp = parts[0]
                    response_time = float(parts[-1].split(':')[-1].replace('s', '').strip())
                    timestamps.append(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S%f'))
                    response_times.append(response_time)

        # Tạo biểu đồ đường (line chart) hiển thị thời gian phản hồi
        line_chart = go.Scatter(x=timestamps, y=response_times, mode='lines', name='Thời gian phản hồi')

        # Chuyển đổi biểu đồ thành định dạng JSON để hiển thị trên giao diện web
        graph_json = json.dumps([line_chart], cls=PlotlyJSONEncoder)  
        return render_template('dashboard.html', graphJSON=graph_json)  
    except Exception as e:
        logger.error(f"Lỗi khi đọc file log: {str(e)}")
        return "Error processing logs.", 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
