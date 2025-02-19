from flask import Blueprint, request, jsonify, request, make_response
from flask_login import login_user, logout_user, login_required
from backend.models.user import User
from backend.services.auth_service import AuthService
from backend.services.email_service import EmailService
from backend.extensions import db
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('auth_token')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            email = AuthService.verify_token(token)
            if not email:
                return jsonify({'error': 'Invalid token'}), 401
            current_user = User.query.filter_by(email=email).first()
            if not current_user:
                return jsonify({'error': 'User not found'}), 404
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': f'Authentication error: {str(e)}'}), 401

    return decorated


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    occupation = data.get('occupation')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({
            'status': 'error',
            'error': 'Email already registered'
        }), 400

    if username and User.query.filter_by(username=username).first():
        return jsonify({
            'status': 'error',
            'error': 'Username already taken'
        }), 400

    user = User(
        email=email,
        username=username,
        occupation=occupation
    )
    user.set_password(password)
    db.session.add(user)

    token = AuthService.generate_verification_token(email)

    if EmailService.send_verification_email(email, token):
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Please check your email for verification.'
        }), 201

    db.session.rollback()
    return jsonify({'error': 'Failed to send verification email'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing email or password'}), 400

        user = User.query.filter_by(email=data.get('email')).first()

        if not user or not user.check_password(data.get('password')):
            return jsonify({
                'status': 'error',
                'error': 'Invalid email or password',
                'message': 'Invalid email or password'
            }), 401

        if not user.is_verified:
            return jsonify({
                'status': 'error',
                'error': 'Please verify your email first',
                'message': 'Please verify your email first'
            }), 401

        token = AuthService.generate_token(user.email)
        if not token:
            return jsonify({'error': 'Error generating authentication token'}), 500

        response = make_response(jsonify({
            'status': 'success',
            'message': 'Logged in successfully',
            'is_verified': user.is_verified,
            'profile': {
                'username': user.username,
                'occupation': user.occupation
            }
        }))

        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            secure=True,
            samesite='None',
            max_age=3600
        )

        return response

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Login failed: {str(e)}'
        }), 500



@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.is_verified:
        return jsonify({'message': 'Email already verified'}), 200

    token = AuthService.generate_verification_token(email)

    if EmailService.send_verification_email(email, token):
        return jsonify({
            'message': 'Verification email sent successfully'
        }), 200
    return jsonify({'error': 'Failed to send verification email'}), 500


@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    try:
        # Verify token and get email
        email = AuthService.verify_token(token)
        if not email:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired verification token'
            }), 400

        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404

        # Check if already verified
        if user.is_verified:
            return jsonify({
                'status': 'success',
                'message': 'Email already verified'
            }), 200

        # Update user verification status
        user.is_verified = True
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Email verified successfully. You can now login.'
        }), 200

    except Exception as e:
        db.session.rollback()  # Rollback on error
        return jsonify({
            'status': 'error',
            'message': f'Verification failed: {str(e)}'
        }), 500


@auth_bp.route('/verification-status', methods=['GET'])
@token_required
def verification_status(current_user):
    try:
        return jsonify({
            'status': 'success',
            'is_verified': current_user.is_verified,
            'email': current_user.email,
            'profile': {
                'username': current_user.username,
                'occupation': current_user.occupation
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error checking verification status: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({
        'status': 'success',
        'message': 'Logged out successfully'
    }))

    # Clear the cookie on the backend
    response.delete_cookie('auth_token',
                           path='/',
                           secure=True,
                           httponly=True,
                           samesite='None')

    return response


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({
                'status': 'error',
                'error': 'Email is required'
            }), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            # For security, don't reveal if email exists
            return jsonify({
                'status': 'success',
                'message': 'If an account exists with this email, you will receive a password reset link.'
            }), 200

        # Generate reset token
        reset_token = AuthService.generate_reset_token(email)

        # Send reset email
        if EmailService.send_reset_email(email, reset_token):
            return jsonify({
                'status': 'success',
                'message': 'Password reset instructions have been sent to your email.'
            }), 200

        return jsonify({
            'status': 'error',
            'error': 'Failed to send reset email'
        }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        data = request.get_json()
        new_password = data.get('password')

        if not new_password:
            return jsonify({
                'status': 'error',
                'error': 'New password is required'
            }), 400

        # Verify token and get email
        email = AuthService.verify_reset_token(token)
        if not email:
            return jsonify({
                'status': 'error',
                'error': 'Invalid or expired reset token'
            }), 400

        # Find user and update password
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'status': 'error',
                'error': 'User not found'
            }), 404

        user.set_password(new_password)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Password has been reset successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
