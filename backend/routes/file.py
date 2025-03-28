from flask import Blueprint, send_from_directory, current_app
from flask_jwt_extended import jwt_required
import os

file_bp = Blueprint('file', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@file_bp.route('/download/<string:filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    """
    Download a file from the uploads directory
    ---
    tags:
      - File Management
    parameters:
      - name: filename
        in: path
        type: string
        required: true
        description: Name of the file to download
    responses:
      200:
        description: File downloaded successfully
      404:
        description: File not found
    """
    file_directory = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(file_directory, filename, as_attachment=True) 