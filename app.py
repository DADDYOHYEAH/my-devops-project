import socket
import os
from datetime import datetime
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    # 1. Fetch System Info (The "Complex" part)
    pod_name = socket.gethostname()
    platform = os.uname().sysname if hasattr(os, 'uname') else 'Windows'
    current_time = datetime.now().strftime("%H:%M:%S")
    date_today = datetime.now().strftime("%Y-%m-%d")

    # 2. Neobrutalist HTML/CSS Template
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Neo-DevOps Monitor</title>
        <style>
            /* Neobrutalism Core Styles */
            :root {
                --bg-color: #ffde59;  /* Bright Yellow */
                --card-bg: #ffffff;   /* White */
                --accent: #ff5757;    /* Red Accent */
                --text: #000000;      /* Pure Black */
                --shadow: 5px 5px 0px 0px #000000; /* Hard Shadow */
                --border: 3px solid #000000;       /* Thick Border */
            }
            body {
                background-color: var(--bg-color);
                font-family: 'Courier New', monospace; /* Retro Font */
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                color: var(--text);
            }
            .container {
                background-color: var(--card-bg);
                border: var(--border);
                box-shadow: var(--shadow);
                width: 450px;
                padding: 30px;
                text-align: left;
                position: relative;
            }
            /* The "Badge" on top right */
            .badge {
                position: absolute;
                top: -15px;
                right: -15px;
                background-color: var(--accent);
                color: white;
                border: var(--border);
                padding: 10px 15px;
                font-weight: bold;
                box-shadow: 3px 3px 0px 0px #000000;
                transform: rotate(2deg);
            }
            h1 {
                font-size: 2.5rem;
                margin: 0 0 20px 0;
                text-transform: uppercase;
                background-color: #5ce1e6; /* Cyan Highlight */
                display: inline-block;
                border: var(--border);
                padding: 5px 10px;
                box-shadow: 3px 3px 0px 0px #000000;
            }
            .stat-box {
                border: var(--border);
                margin-top: 15px;
                padding: 15px;
                background-color: #f4f4f4;
                transition: transform 0.1s;
            }
            .stat-box:hover {
                transform: translate(-2px, -2px);
                box-shadow: 3px 3px 0px 0px #000000;
                background-color: #cb9bf7; /* Purple on hover */
            }
            .label { font-weight: bold; text-transform: uppercase; font-size: 0.8rem; }
            .value { font-size: 1.2rem; display: block; margin-top: 5px; }
            .footer { margin-top: 30px; font-size: 0.8rem; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="badge">V4.0 LIVE</div>
            <h1>System Monitor</h1>
            
            <p><strong>Orchestration Level:</strong> KUBERNETES</p>
            <p><strong>Status:</strong> <span style="background:black; color:white; padding:2px 5px;">OPERATIONAL</span></p>

            <div class="stat-box">
                <span class="label">Pod Identity (Hostname)</span>
                <span class="value">{{ pod_name }}</span>
            </div>

            <div class="stat-box">
                <span class="label">OS Platform</span>
                <span class="value">{{ platform }}</span>
            </div>

            <div class="stat-box">
                <span class="label">Server Timestamp</span>
                <span class="value">{{ date_today }} | {{ current_time }}</span>
            </div>

            <div class="footer">
                // DEVOPS_PROJECT_FINAL //
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content, pod_name=pod_name, current_time=current_time, date_today=date_today, platform=platform)

@app.route('/feature')
def feature():
    return "Neobrutalism Marketing Feature Active"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 