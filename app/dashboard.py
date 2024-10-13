from flask import Flask, render_template
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
from datetime import datetime
import os

app = Flask(__name__)

# API phân tích hiệu suất và tạo biểu đồ
@app.route('/dashboard')
def dashboard():
    response_times = []
    timestamps = []
   
    log_file_path = 'logs/api_requests.log'
   
    if not os.path.exists(log_file_path):
        return "Log file not found.", 404

    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            if 'Thời gian phản hồi' in line:
                parts = line.split(' - ')
                timestamp = parts[0]
                response_time = float(parts[-1].split(':')[-1].replace('s', '').strip())
                timestamps.append(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S%f'))
                response_times.append(response_time)

    # Kiểm tra xem có dữ liệu không
    if len(response_times) == 0 or len(timestamps) == 0:
        return render_template('dashboard.html', graph_json=json.dumps({}))  # Không có dữ liệu, trả về biểu đồ rỗng

    # Tạo biểu đồ khi có dữ liệu
    line_chart = go.Scatter(x=timestamps, y=response_times, mode='lines', name='Thời gian phản hồi')
    graph_json = json.dumps(go.Figure(data=[line_chart]), cls=PlotlyJSONEncoder)

    return render_template('dashboard.html', graph_json=graph_json)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
