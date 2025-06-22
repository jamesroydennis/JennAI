# /home/jdennis/Projects/JennAI/src/presentation/api_server/flask_app/blueprints/image_processing_api.py
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from loguru import logger

# Import the celery task
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

        # Save the uploaded file to the input directory
        file.save(input_path)
        logger.info(f"File '{filename}' saved to '{input_path}'.")
        
        # --- Dispatch the ML processing task to the Celery worker ---
        logger.info(f"Dispatching task to Celery for effect '{effect}' on file '{input_path}'.")
        task = process_media_file.delay(
            input_path=input_path,
            output_path=output_path,
            effect=effect
        )
        
        # Return 202 Accepted to indicate the request is being processed asynchronously.
        return jsonify({
            "message": "File received and accepted for processing.",
            "job_id": task.id # The Celery task ID for the client to track status
        }), 202

    logger.warning(f"API call to /media with disallowed file type: {file.filename}")
    return jsonify({"error": "File type not allowed"}), 400