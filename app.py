import socket
from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    # Get the Pod Name (Hostname)
    pod_name = socket.gethostname()
    # Get current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # HTML Template with "Dark Mode" CSS
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevOps Dashboard</title>
        <style>
            body {
                background-color: #1e1e2f;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .dashboard {
                background-color: #27293d;
                width: 400px;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                text-align: center;
                border: 1px solid #3d405b;
            }
            h1 { color: #e14eca; margin-bottom: 10px; }
            .status {
                background-color: #00f2c3;
                color: #1e1e2f;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
                margin-bottom: 20px;
                font-size: 0.9em;
            }
            .info-box {
                background-color: #1e1e2f;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #e14eca;
                text-align: left;
            }
            .label { color: #8d8d8d; font-size: 0.8em; display: block; }
            .value { font-size: 1.1em; font-weight: 500; }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="status">● System Operational</div>
            <h1>DevOps Dashboard</h1>
            <p>Welcome to the V3 Enterprise Interface</p>
            
            <div class="info-box">
                <span class="label">Running on Pod ID:</span>
                <span class="value">{{ pod_name }}</span>
            </div>

            <div class="info-box">
                <span class="label">Server Time:</span>
                <span class="value">{{ current_time }}</span>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content, pod_name=pod_name, current_time=current_time)

@app.route('/feature')
def feature():
    return "This is the new Marketing Feature!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)