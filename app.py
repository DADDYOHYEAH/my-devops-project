import socket
import os
from datetime import datetime
from flask import Flask, render_template_string

app = Flask(__name__)

# --- NEOBRUTALISM TEMPLATE (Fixed) ---
# Notice we use a unique placeholder "" instead of Jinja blocks
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DevOps Project V4</title>
    <style>
        /* CORE VARIABLES */
        :root {
            --bg-color: #ffde59;  /* Bright Yellow */
            --card-bg: #ffffff;   /* White */
            --accent: #ff5757;    /* Red Accent */
            --nav-bg: #5ce1e6;    /* Cyan */
            --text: #000000;
            --shadow: 5px 5px 0px 0px #000000;
            --border: 3px solid #000000;
        }
        body {
            background-color: var(--bg-color);
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            color: var(--text);
        }
        /* NAVIGATION */
        .nav-bar {
            background: var(--nav-bg);
            border: var(--border);
            box-shadow: var(--shadow);
            padding: 15px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .nav-links a {
            text-decoration: none;
            color: black;
            font-weight: bold;
            font-size: 1.2rem;
            margin-left: 20px;
            padding: 5px 10px;
            border: 2px solid transparent;
        }
        .nav-links a:hover {
            background: white;
            border: 2px solid black;
            box-shadow: 2px 2px 0px 0px black;
        }
        
        /* CONTAINER */
        .container {
            background-color: var(--card-bg);
            border: var(--border);
            box-shadow: var(--shadow);
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            position: relative;
        }
        h1 {
            background-color: var(--accent);
            color: white;
            display: inline-block;
            padding: 10px;
            border: var(--border);
            box-shadow: 3px 3px 0px 0px black;
            text-transform: uppercase;
        }
        .stat-box {
            border: 2px solid black;
            background: #f4f4f4;
            padding: 15px;
            margin: 10px 0;
            font-weight: bold;
        }
        .stat-box:hover {
            background: #cb9bf7;
            transform: translate(-2px, -2px);
            box-shadow: 3px 3px 0px 0px black;
        }
        .footer { margin-top: 40px; font-size: 0.8rem; border-top: 2px solid black; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="nav-bar">
        <div style="font-weight:900; font-size:1.5rem;">MY_DEVOPS_PROJECT</div>
        <div class="nav-links">
            <a href="/">HOME</a>
            <a href="/dashboard">DASHBOARD</a>
            <a href="/team">TEAM</a>
        </div>
    </div>

    <div class="container">
        </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Page specific HTML
    page_content = """
        <h1>Welcome to V4.0</h1>
        <p style="font-size: 1.2rem;">
            This is a fully automated, high-availability web application deployed using Kubernetes.
        </p>
        <div class="stat-box" style="background:#5ce1e6;">
            🚀 CI/CD Pipeline Active
        </div>
        <div class="stat-box" style="background:#ff5757; color:white;">
            🛡️ Security Scanned & Hardened
        </div>
        <div class="stat-box" style="background:#ffde59;">
            ⚖️ Auto-Scaling Enabled
        </div>
    """
    # Merge the base template with the page content
    final_html = BASE_TEMPLATE.replace("", page_content)
    return render_template_string(final_html)

@app.route('/dashboard')
def dashboard():
    # Fetch System Info
    pod_name = socket.gethostname()
    platform = os.uname().sysname if hasattr(os, 'uname') else 'Windows'
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Page specific HTML
    page_content = """
        <h1>System Monitor</h1>
        <p>Real-time metrics from the containerized environment.</p>
        
        <div class="stat-box">
            <span>POD ID:</span> <span style="float:right;">{{ pod_name }}</span>
        </div>
        <div class="stat-box">
            <span>SERVER OS:</span> <span style="float:right;">{{ platform }}</span>
        </div>
        <div class="stat-box">
            <span>TIME:</span> <span style="float:right;">{{ current_time }}</span>
        </div>
    """
    
    # Merge first, then render (so {{ pod_name }} gets filled)
    final_html = BASE_TEMPLATE.replace("", page_content)
    return render_template_string(final_html, pod_name=pod_name, platform=platform, current_time=current_time)

@app.route('/team')
def team():
    # Page specific HTML
    page_content = """
        <h1>Meet the Team</h1>
        <p>The engineers behind this DevOps infrastructure.</p>
        <ul>
            <li><strong>Lead DevOps Engineer:</strong> DaddyOhYeah</li>
            <li><strong>QA Specialist:</strong> [Your Name]</li>
            <li><strong>Site Reliability Engineer:</strong> [Your Name]</li>
        </ul>
    """
    final_html = BASE_TEMPLATE.replace("", page_content)
    return render_template_string(final_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)