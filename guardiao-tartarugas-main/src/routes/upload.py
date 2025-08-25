from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from src.routes.auth import login_required
import os
import uuid

upload_bp = Blueprint('upload', __name__)
UPLOAD_FOLDER = 'uploads'

def ensure_upload_folder():
    upload_path = os.path.join(current_app.static_folder, UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

@upload_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files or not request.files['file'].filename:
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in {'png', 'jpg', 'jpeg', 'gif'}:
        return jsonify({'error': 'Tipo de arquivo não permitido.'}), 400

    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    upload_path = ensure_upload_folder()
    file.save(os.path.join(upload_path, unique_filename))
    
    return jsonify({'file_path': f"{UPLOAD_FOLDER}/{unique_filename}"}), 200

@upload_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(current_app.static_folder, UPLOAD_FOLDER), filename)