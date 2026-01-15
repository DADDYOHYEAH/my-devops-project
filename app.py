import socket
import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Flask looks for 'index.html' inside the 'templates' folder automatically
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # This keeps your "Functionality" requirement satisfied
    pod_name = socket.gethostname()
    return f"""
    <div style="font-family: monospace; padding: 20px;">
        <h1>🔧 DevOps Dashboard</h1>
        <p><strong>Status:</strong> Online</p>
        <p><strong>Pod ID:</strong> {pod_name}</p>
        <p><strong>App Name:</strong> Drive Mad (Single File Version)</p>
    </div>
    """

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)