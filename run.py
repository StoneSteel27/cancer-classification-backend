import os
from flask import Flask
from flask_cors import CORS
from backend.config.production import ProductionConfig
from backend.extensions import db, login_manager
from backend.routes.auth_routes import auth_bp
from backend.routes.prediction_routes import pred_bp
from backend.routes.profile_routes import profile_bp
from backend.error_handlers import errors
import logging
from logging.handlers import RotatingFileHandler


def create_app(config_class=ProductionConfig):
    app = Flask(__name__)

    # Configure logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/cancer_classification.log',
                                       maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Cancer Classification startup')

    # Configure CORS for production
    CORS(app, resources={
        r"/*": {
            "origins": ["https://.com"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "supports_credentials": True,
            "max_age": 120
        }
    })

    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(pred_bp, url_prefix='/api')
    app.register_blueprint(profile_bp)
    app.register_blueprint(errors)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Add security headers
    @app.after_request
    def add_security_headers(response):
        for header, value in app.config['SECURE_HEADERS'].items():
            response.headers[header] = value
        return response

    return app


app = create_app()

if __name__ == '__main__':
    # In production, you'll typically use a WSGI server like gunicorn
    app.run(host='0.0.0.0', port=5000)