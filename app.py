import socket
import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/yes_page.html')
def yes_page():
    return render_template('yes_page.html')

@app.route('/dashboard')
def dashboard():
    # KEEPS YOUR DEVOPS MARKS SAFE
    pod_name = socket.gethostname()
    return f"<h1>Ops Dashboard</h1><p>Running on Pod: {pod_name}</p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)