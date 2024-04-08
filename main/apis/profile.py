import os
from flask import Blueprint, jsonify, request, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.main.validators.validators import Validators
from app.utils import allowed_file
from werkzeug.utils import secure_filename
from app.model import db, User

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        abort(404, 'User not found')

    if request.method == 'GET':
        followers_count = user.count_followers()
        following_count = user.count_following()

        return jsonify({
            'username': user.username,
            'email': user.email,
            'profile_picture': user.profile_picture,
            'followers': followers_count,
            'following': following_count
        }), 200
  
    elif request.method == 'PUT':
        data = request.json

        validation_result = Validators.check_profile_update_required_fields(data)
        if validation_result["status"] != 200:
            return jsonify(validation_result), validation_result["status"]

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.role = data.get('role', user.role)

        db.session.commit()

        return jsonify({'message': 'Profile updated successfully'}), 200

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'User deleted successfully'}), 200


@profile_bp.route('/picture', methods=['PUT'])
@jwt_required()
def update_profile_picture():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        abort(404, 'User not found')

    if 'profile_picture' not in request.files:
        abort(400, 'No profile picture provided')

    profile_picture = request.files['profile_picture']

    if profile_picture.filename == '':
        abort(400, 'No selected file')

    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    if profile_picture and allowed_file(profile_picture.filename, allowed_extensions):
        filename = secure_filename(profile_picture.filename)
        profile_picture.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        user.profile_picture = filename
        db.session.commit()

        return jsonify({'message': 'Profile picture updated successfully'}), 200
    else:
        abort(400, 'Invalid file type for profile picture')