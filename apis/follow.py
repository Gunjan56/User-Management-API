from flask import (jsonify, abort, g)
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from dotenv import load_dotenv, dotenv_values
from models.model import User, db, Follow
load_dotenv()

from flask import Blueprint
bp = Blueprint('follow', __name__)
@bp.route('/follow/<int:user_id>', methods=['POST'])
@jwt_required()
def follow(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    target_user = User.query.get(user_id)

    if not current_user or not target_user:
        abort(404, 'User not found')

    if current_user.id == target_user.id:
        abort(400, 'Cannot follow yourself')


    follow = Follow(
        follower_id=current_user.id,
        followed_id=user_id
    )
    
    db.session.add(follow)
    db.session.commit()

    return jsonify({'message': 'Successfully followed'}), 200

@bp.route('/unfollow/<int:user_id>', methods=['POST'])
@jwt_required()
def unfollow(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    target_user = User.query.get(user_id)

    if not current_user or not target_user:
        abort(404, 'User not found')

    follow = Follow.query.filter_by(
        follower_id=current_user.id,
        followed_id=user_id
    ).first()

    if not follow:
        abort(404, 'You are not following this user')

    db.session.delete(follow)
    db.session.commit()

    return jsonify({'message': 'Unfollowed successfully'}), 200
