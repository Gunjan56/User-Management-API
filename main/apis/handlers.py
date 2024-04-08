from flask import Flask, jsonify, Blueprint
import flask
handlers_bp = Blueprint("error", __name__)

@handlers_bp.app_errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request'}), 400

@handlers_bp.app_errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@handlers_bp.app_errorhandler(403)
def forbidden(error):
    print(error)
    return jsonify({'error': 'Forbidden'}, ), 403

@handlers_bp.app_errorhandler(404)
def page_not_found(error):
    return jsonify({'error': 'Not Found'}), 404