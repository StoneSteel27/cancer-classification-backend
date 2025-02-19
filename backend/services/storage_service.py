import os
import uuid
from datetime import datetime
from flask import current_app, url_for
from werkzeug.utils import secure_filename


class StorageService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in StorageService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_image(file):
        if not file or not StorageService.allowed_file(file.filename):
            return None

        # Generate unique filename
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{extension}"

        # Create year/month based directory structure
        current_date = datetime.now()

        # Create filesystem path with os.path.join
        relative_path_parts = [
            'uploads',
            str(current_date.year),
            str(current_date.month).zfill(2)
        ]

        # Use os.path.join for filesystem operations
        upload_path = os.path.join(current_app.root_path, 'static', *relative_path_parts)
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)

        # Create URL path with forward slashes explicitly
        url_path = '/'.join(relative_path_parts + [unique_filename])

        # Replace any remaining backslashes with forward slashes
        url_path = url_path.replace('\\', '/')

        return url_path

    @staticmethod
    def get_image_url(image_path):
        if not image_path:
            return None
        # Just return the relative path, don't use url_for here
        return image_path