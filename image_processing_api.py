# /home/jdennis/Projects/JennAI/src/presentation/api_server/flask_app/blueprints/image_processing_api.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from loguru import logger

# Import the celery task and the celery app instance
from celery_app import celery_app
from src.business.tasks.ml_tasks import process_media_file

# Create a Blueprint for image processing endpoints
image_processing_bp = Blueprint(
    'image_processing_bp', 
    __name__,
    url_prefix='/api/v1/process'
)

# In a real app, these would come from a config file or environment variables.
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'results'

# Define allowed extensions for security
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    """Checks if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@image_processing_bp.route('/media', methods=['POST'])
def process_media():
    """
    API endpoint to upload an image or video and apply an ML effect.
    Expects a multipart/form-data request with a 'file' and an 'effect' field.
    """
    if 'file' not in request.files:
        logger.warning("API call to /media missing file part.")
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("API call to /media with no selected file.")
        return jsonify({"error": "No selected file"}), 400

    effect = request.form.get('effect')
    if not effect:
        return jsonify({"error": "No 'effect' specified in form data"}), 400

    # Ensure upload and output directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")

        file.save(input_path)
        logger.info(f"File '{filename}' saved to '{input_path}'.")
        
        logger.info(f"Dispatching task to Celery for effect '{effect}' on file '{input_path}'.")
        task = process_media_file.delay(input_path=input_path, output_path=output_path, effect=effect)
        
        return jsonify({
            "message": "File received and accepted for processing.",
            "job_id": task.id
        }), 202

    logger.warning(f"API call to /media with disallowed file type: {file.filename}")
    return jsonify({"error": "File type not allowed"}), 400

@image_processing_bp.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id: str):
    """API endpoint to check the status of a background processing job."""
    logger.info(f"API call to check status for job_id: {job_id}")
    task = celery_app.AsyncResult(job_id)

    response = {'job_id': job_id, 'status': task.state, 'result': task.result if task.state == 'SUCCESS' else str(task.info)}
    return jsonify(response), 200