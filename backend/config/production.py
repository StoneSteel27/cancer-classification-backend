# backend/config/production.py

import os
from backend.config.config import Config


class ProductionConfig(Config):
    # Security settings
    DEBUG = False
    TESTING = False

    # HTTPS settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    # Cookie settings
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Database settings (SQLite)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security headers
    SECURE_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline';",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
