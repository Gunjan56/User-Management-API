from flask import Flask, jsonify, Blueprint
bp = Blueprint('error', __name__)
@bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request'}), 400

@bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@bp.errorhandler(403)
def forbidden(error):
    print(error)
    return jsonify({'error': 'Forbidden'}, ), 403

@bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404
