from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello! This is Version 1 of our application."

@app.route('/feature')
def feature():
    return "This is the new Marketing Feature!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)