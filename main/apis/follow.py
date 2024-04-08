from flask import Blueprint, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.model import db, User, Follow
from app.main.validators.validators import Validators

follow_bp = Blueprint('follow', __name__)

@follow_bp.route('/follow/<int:user_id>', methods=['POST'])
@jwt_required()
def follow(user_id):
    current_user_id = get_jwt_identity()

    validation_result = Validators.validate_user_id(user_id)
    if validation_result["status"] != 200:
        return jsonify(validation_result), validation_result["status"]

    if current_user_id == user_id:
        abort(400, 'Cannot follow yourself')

    follow = Follow(
        follower_id=current_user_id,
        followed_id=user_id
    )
    
    db.session.add(follow)
    db.session.commit()

    return jsonify({'message': 'Successfully followed'}), 200

@follow_bp.route('/unfollow/<int:user_id>', methods=['POST'])
@jwt_required()
def unfollow(user_id):
    current_user_id = get_jwt_identity()

    validation_result = Validators.validate_user_id(user_id)
    if validation_result["status"] != 200:
        return jsonify(validation_result), validation_result["status"]

    follow = Follow.query.filter_by(
        follower_id=current_user_id,
        followed_id=user_id
    ).first()

    if not follow:
        abort(404, 'You are not following this user')

    db.session.delete(follow)
    db.session.commit()

    return jsonify({'message': 'Unfollowed successfully'}), 200

