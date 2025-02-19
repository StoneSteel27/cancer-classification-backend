from flask import Blueprint, request, jsonify, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from backend.services.ml_service import MLService
from backend.services.storage_service import StorageService
from backend.models.prediction import Prediction
from backend.extensions import db
from backend.routes.auth_routes import token_required
import os

pred_bp = Blueprint('predictions', __name__)


@pred_bp.route('/predict', methods=['POST'])
@token_required
def predict(current_user):
    if 'files' not in request.files:
        return jsonify({
            'status': 'error',
            'error': 'missing_files',
            'message': 'No images uploaded'
        }), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({
            'status': 'error',
            'error': 'Please select valid image files to analyze.'
        }), 400

    # Validate number of files
    if len(files) > 5:
        return jsonify({
            'status': 'error',
            'error': 'too_many_files',
            'message': 'Maximum 5 images allowed'
        }), 400

    try:
        ml_service = MLService()
        predictions = []
        errors = []

        for file in files:
            # Validate file type
            if not StorageService.allowed_file(file.filename):
                errors.append(f'File "{file.filename}" is not supported. Please use PNG, JPG or JPEG images.')
                continue

            # Validate file size
            if len(file.read()) > current_app.config['MAX_CONTENT_LENGTH']:
                errors.append(f'File "{file.filename}" exceeds the maximum size limit of 16MB.')
                continue
            file.seek(0)  # Reset file pointer

            try:
                # Save the image
                image_path = StorageService.save_image(file)
                if not image_path:
                    errors.append(f'Failed to save file "{file.filename}". Please try again.')
                    continue

                # Get prediction
                result = ml_service.predict_image(file)

                # Validate prediction result
                if 'error' in result:
                    errors.append(f'Failed to analyze "{file.filename}": {result["error"]}')
                    continue

                # Save prediction to database
                prediction = Prediction(
                    user_id=current_user.id,
                    image_path=image_path,
                    prediction_result=result['prediction'],
                    confidence=result['confidence']
                )
                db.session.add(prediction)

                predictions.append({
                    'filename': file.filename,
                    'prediction': result['prediction'],
                    'confidence': result['confidence'],
                    'image_url': f"http://localhost:5000/api/image/{image_path}"
                })

            except Exception as e:
                errors.append(f'Error processing "{file.filename}": {str(e)}')
                continue

        # Commit successful predictions to database
        if predictions:
            db.session.commit()

        response = {
            'status': 'success' if predictions else 'error',
            'predictions': predictions,
        }

        if errors:
            response['errors'] = errors
            if not predictions:
                return jsonify(response), 400

        return jsonify(response)

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': 'An unexpected error occurred. Please try again.',
            'details': str(e)
        }), 500


@pred_bp.route('/history', methods=['GET'])
@token_required
def get_prediction_history(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(int(request.args.get('per_page', 10)), 50)  # Limit max items per page

        predictions = Prediction.query.filter_by(user_id=current_user.id) \
            .order_by(Prediction.timestamp.desc()) \
            .paginate(page=page, per_page=per_page)

        history = [{
            'id': pred.id,
            'image_url': f"http://localhost:5000/api/image/{pred.image_path}",
            'prediction': pred.prediction_result,
            'confidence': pred.confidence,
            'timestamp': pred.timestamp.isoformat(),
            'date_formatted': pred.timestamp.strftime('%B %d, %Y %I:%M %p')
        } for pred in predictions.items]

        return jsonify({
            'status': 'success',
            'predictions': history,
            'total': predictions.total,
            'pages': predictions.pages,
            'current_page': page,
            'has_next': predictions.has_next,
            'has_prev': predictions.has_prev
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch prediction history.',
            'details': str(e)
        }), 500


@pred_bp.route('/image/<path:filename>')
@token_required
def serve_image(current_user, filename):
    try:
        # Clean up the filename by removing any URL components
        filename = filename.replace('http://localhost:5000/api/image/', '')

        # Verify the image belongs to the current user
        prediction = Prediction.query.filter_by(
            user_id=current_user.id
        ).filter(Prediction.image_path.like(f'%{filename}')).first()

        if not prediction:
            return jsonify({
                'status': 'error',
                'error': 'You do not have permission to access this image.'
            }), 403

        # Construct the full path to the image
        image_path = os.path.join(current_app.root_path, 'static', filename)

        # Basic security check
        if not os.path.normpath(image_path).startswith(
                os.path.normpath(os.path.join(current_app.root_path, 'static'))
        ):
            return jsonify({
                'status': 'error',
                'error': 'Invalid image path.'
            }), 403

        if not os.path.exists(image_path):
            return jsonify({
                'status': 'error',
                'error': 'Image not found.'
            }), 404

        return send_from_directory(
            os.path.dirname(image_path),
            os.path.basename(image_path),
            as_attachment=False
        )

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve image.',
            'details': str(e)
        }), 500

