from flask import Flask, render_template
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
from datetime import datetime

app = Flask(__name__)

# API phân tích hiệu suất và tạo biểu đồ
@app.route('/dashboard')
def dashboard():
    # Đọc dữ liệu từ file log
    response_times = []
    timestamps = []
    
    with open('logs/api_requests.log', 'r') as log_file:
        for line in log_file:
            if 'Thời gian phản hồi' in line:
                parts = line.split(' - ')
                timestamp = parts[0]
                response_time = float(parts[-1].split(':')[-1].replace('s', '').strip())
                timestamps.append(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f'))
                response_times.append(response_time)

    # Tạo biểu đồ đường (line chart) hiển thị thời gian phản hồi
    line_chart = go.Scatter(x=timestamps, y=response_times, mode='lines', name='Thời gian phản hồi')

    # Chuyển đổi biểu đồ thành định dạng JSON để hiển thị trên giao diện web
    graphJSON = json.dumps([line_chart], cls=PlotlyJSONEncoder)

    return render_template('dashboard.html', graphJSON=graphJSON)

if __name__ == '__main__':
    app.run(debug=True)
