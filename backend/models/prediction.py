from datetime import datetime
from backend.extensions import db


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)  # Store relative path
    prediction_result = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def image_url(self):
        from backend.services.storage_service import StorageService
        return StorageService.get_image_url(self.image_path)
