from flask import Flask, request, redirect
import subprocess
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return open("upload.html").read()

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['botfile']
    if file.filename.endswith('.py'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        # Run the bot in a new process
        subprocess.Popen(["python", filepath])
        return "Bot is running!"
    return "Invalid file"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
