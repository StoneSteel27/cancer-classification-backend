import jwt
from datetime import datetime, timedelta
from flask import current_app
from backend.models.user import User
from backend.extensions import db


class AuthService:
    @staticmethod
    def generate_token(email):
        try:
            token = jwt.encode(
                {
                    'email': email,
                    'exp': datetime.utcnow() + timedelta(hours=1),  # Token expires in 1 hour
                    'iat': datetime.utcnow()
                },
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            return token
        except Exception as e:
            print(f"Auth token generation error: {e}")
            return None

    @staticmethod
    def generate_verification_token(email):
        try:
            token = jwt.encode(
                {
                    'email': email,
                    'exp': datetime.utcnow() + timedelta(hours=24),
                    'iat': datetime.utcnow(),
                    'type': 'verification'  # Add token type to distinguish from auth tokens
                },
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            return token
        except Exception as e:
            print(f"Token generation error: {e}")
            return None

    @staticmethod
    def verify_token(token):
        if not token:
            return None

        try:
            data = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )

            # Check if token has required claims
            if 'email' not in data:
                return None

            # Check if token is expired
            exp = datetime.fromtimestamp(data['exp'])
            if datetime.utcnow() > exp:
                return None

            return data['email']
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return None
        except Exception as e:
            print(f"Token verification error: {e}")
            return None

    @staticmethod
    def create_user(email, password):
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def generate_reset_token(email):
        try:
            token = jwt.encode(
                {
                    'email': email,
                    'exp': datetime.utcnow() + timedelta(hours=1),  # Reset token expires in 1 hour
                    'iat': datetime.utcnow(),
                    'type': 'reset'  # Add token type to distinguish from other tokens
                },
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            return token
        except Exception as e:
            print(f"Reset token generation error: {e}")
            return None

    @staticmethod
    def verify_reset_token(token):
        if not token:
            return None

        try:
            data = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )

            # Check if token has required claims and is reset token
            if 'email' not in data or data.get('type') != 'reset':
                return None

            # Check if token is expired
            exp = datetime.fromtimestamp(data['exp'])
            if datetime.utcnow() > exp:
                return None

            return data['email']
        except Exception as e:
            print(f"Reset token verification error: {e}")
            return None
