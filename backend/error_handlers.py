from flask import jsonify, Blueprint

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error)}), 400


@errors.app_errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401


@errors.app_errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': str(error)}), 403


@errors.app_errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': str(error)}), 404


@errors.app_errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': 'Something went wrong'}), 500
