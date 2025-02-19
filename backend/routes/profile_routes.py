from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models.user import User
from backend.routes.auth_routes import token_required

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/auth/update-username', methods=['PUT'])
@token_required
def update_username(current_user):
    try:
        data = request.get_json()
        username = data.get('username')

        if not username:
            return jsonify({
                'status': 'error',
                'error': 'Username is required'
            }), 400

        # Check if username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            return jsonify({
                'status': 'error',
                'error': 'Username is already taken'
            }), 400

        current_user.username = username
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Username updated successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@profile_bp.route('/auth/update-occupation', methods=['PUT'])
@token_required
def update_occupation(current_user):
    try:
        data = request.get_json()
        occupation = data.get('occupation')

        if not occupation:
            return jsonify({
                'status': 'error',
                'error': 'Occupation is required'
            }), 400

        current_user.occupation = occupation
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Occupation updated successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@profile_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        return jsonify({
            'status': 'success',
            'profile': {
                'email': current_user.email,
                'username': current_user.username,
                'occupation': current_user.occupation,
                'is_verified': current_user.is_verified
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
