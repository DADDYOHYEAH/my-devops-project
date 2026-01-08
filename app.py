from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>DevOps Demo</title>
        <style>
            body {
                background-color: #f0f2f5;
                font-family: 'Arial', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background-color: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
            }
            h1 { color: #1a73e8; }
            p { color: #5f6368; font-size: 18px; }
            .version {
                margin-top: 20px;
                display: inline-block;
                padding: 5px 10px;
                background-color: #e8f0fe;
                color: #1a73e8;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚀 DevOps Master</h1>
            <p>Welcome to my final project submission!</p>
            <p>This app is running on <b>Kubernetes</b>.</p>
            <div class="version">Version 2.0</div>
        </div>
    </body>
    </html>
    """

@app.route('/feature')
def feature():
    return "This is the new Marketing Feature!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)