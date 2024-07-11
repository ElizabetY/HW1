import time

from flask import Blueprint, request, jsonify, current_app, render_template, url_for
from werkzeug.utils import secure_filename
from flask_login import login_required
import os
from ultralytics import YOLO

upload = Blueprint('upload', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload.route('/upload', methods=['GET'])
@login_required
def upload_form():
    return render_template('upload.html')

@upload.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            current_app.config['BAD'] += 1
            return jsonify({'error': {'code': 400, 'message': 'No file part'}}), 400
        file = request.files['file']
        if file.filename == '':
            current_app.config['BAD'] += 1
            return jsonify({'error': {'code': 400, 'message': 'No selected file'}}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            try:
                # Use YOLOv8 to process the uploaded image
                model = YOLO('yolov8n.pt')  # Load the YOLOv8 model
                results = model(file_path)  # Perform inference on the uploaded image
                detections = results[0].boxes.data.cpu().numpy()  # Extract detection data

                # Process detections to format the response
                class_names = model.names  # Class names from the YOLO model
                matches = [{'name': class_names[int(detection[5])], 'score': float(detection[4])} for detection in detections]
                if 'application/json' in request.headers.get('Accept', ''):
                    current_app.config['GOOD'] += 1
                    return jsonify({'matches': matches}), 200
                else:
                    current_app.config['GOOD'] += 1
                    return render_template('upload.html', objects=matches, filename=filename)
            except Exception as e:
                current_app.config['BAD'] += 1
                return jsonify({'error': {'code': 500, 'message': str(e)}}), 500
        elif not allowed_file(file.filename):
            current_app.config['BAD'] += 1
            return jsonify({'error': {'code': 400, 'message': 'File type not allowed'}}), 400
    # Handle unauthorized access (if the function continues to execute)
    return jsonify({'error': {'code': 401, 'message': 'Unauthorized access'}}), 401



@upload.route('/result/', methods=['GET'])
def get_result():
    return jsonify({'error': {'code': 404, 'message': 'Result not found'}}), 404

@upload.route('/status', methods=['GET'])
def status():
    status_info = {
        'uptime': (time.time()) - (current_app.config['UPTIME']),
        'processed': {
            'success': current_app.config['GOOD'],
            'fail': current_app.config['BAD'],
            'running': 0,
            'queued': 0
        },
        'health': 'ok',
        'api_version': 1
    }
    return jsonify(status_info), 200
