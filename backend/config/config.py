import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Frontend URL for email verification
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    # Email Configuration
    GMAIL_CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                          'credentials.json')
    GMAIL_TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'token.pickle')
    GMAIL_SENDER = "contactdrsuzane@gmail.com"  # Your Gmail address

    # Email Verification Token Expiry (in hours)
    EMAIL_TOKEN_EXPIRY = 24

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # ML Model Configuration
    MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'best_model.h5')
    IMAGE_SIZE = (224, 224)
    CLASS_LABELS = ['Cancer', 'Normal']

    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'protected', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
