from flask import Flask, render_template, Response, request
import os
import cv2
import numpy as np
from core_logic import VehicleCounter

app = Flask(__name__)
upload_folder = "uploads"
os.makedirs(upload_folder, exist_ok=True)

video_path = os.path.join(upload_folder, "input.mp4")
zones = []
counter = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global video_path, counter, zones
    file = request.files['video']
    video_path = os.path.join(upload_folder, "input.mp4")
    file.save(video_path)
    zones.clear()
    counter = VehicleCounter(video_path)
    return 'Uploaded', 200

@app.route('/click', methods=['POST'])
def click():
    global zones
    x, y = int(request.form['x']), int(request.form['y'])
    zones.append((x, y))
    return 'OK', 200

def generate():
    global counter
    for frame in counter.run(zones):
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render uses PORT env variable
    app.run(host='0.0.0.0', port=port)
