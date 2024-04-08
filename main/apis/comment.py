from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.model import db, User, Post, Comment
from app.main.validators.validators import Validators

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    post = Post.query.get(post_id)

    if not current_user or not post:
        abort(404, 'User or Post not found')

    data = request.json
    validation_result = Validators.validate_comment_data(data)
    if validation_result["status"] != 200:
        return jsonify(validation_result), validation_result["status"]

    new_comment = Comment(
        user_id=current_user_id,
        post_id=post_id,
        content=data['content']
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'message': 'Comment added successfully'}), 201

@comment_bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(post_id, comment_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    post = Post.query.get(post_id)

    if not current_user or not post:
        abort(404, 'User or Post not found')

    comment = Comment.query.filter_by(
        id=comment_id,
        post_id=post_id
    ).first()

    validation_result = Validators.validate_comment_delete(comment, current_user_id)
    if validation_result["status"] != 200:
        return jsonify(validation_result), validation_result["status"]

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'message': 'Comment deleted successfully'}), 200
