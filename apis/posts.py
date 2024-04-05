import os
from flask import (request,jsonify, abort, g, send_from_directory)
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from dotenv import load_dotenv, dotenv_values
from app.utils.decorator import roles_required
from app.models.model import User, db, Post, Comment, Liked_Post
load_dotenv()

from flask import Blueprint
from app.config import Configuration
bp = Blueprint('post', __name__)
@bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        abort(404, 'user not found')

    data = request.json

    content = data.get('content')

    if not content:
        abort(400, 'Content is required')

    new_post = Post(
        content=content,
        user_id=current_user_id
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created successfully'}), 201

@bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@jwt_required()
@roles_required('administrator')
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, 'User not found')
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


@bp.route('/manage_post/<int:post_id>', methods=['GET', 'PUT'])
@jwt_required()
def manage_post(post_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        abort(404, 'User not found')

    post = Post.query.get(post_id)

    if not post:
        abort(404, 'Post not found')

    if post.user_id != current_user_id:
        abort(403, 'You are not authorized')

    if request.method == 'GET':
        return jsonify({
            'id': post.id,
            'content': post.content
        }), 200

    elif request.method == 'PUT':
        data = request.json

        content = data.get('content', post.content)
        db.session.commit()

        return jsonify({'message': 'Post updated successfully'}), 200


@bp.route('/delete_post/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    current_user_id = get_jwt_identity()
    post = Post.query.get(post_id)
    if not post:
        abort(404, 'Post not found')
    user = User.query.get(current_user_id)
    if not user:
        abort(404, 'User not found')

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'}), 200

@bp.route('/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    post = Post.query.get(post_id)
    if not current_user or not post:
        abort(404, 'User or Post not found')

    like = Liked_Post(
        user_id=current_user_id,
        post_id=post.id,
        is_like = True
    )
    db.session.add(like)
    db.session.commit()
    return jsonify({'message': 'post liked'}), 200

@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    post = Post.query.get(post_id)

    if not current_user or not post:
        abort(404, 'User or Post not found')

    content = request.json.get('content')

    if not content:
        abort(400, 'Content is required')

    new_comment = Comment(
        user_id=current_user_id,
        post_id=post_id,
        content=content
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'message': 'Comment added successfully'}), 201

@bp.route('/posts/<int:post_id>/delete_comment/<int:comment_id>', methods=['DELETE'])
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

    if not comment:
        abort(404, 'Comment not found')

    if comment.user_id != current_user_id:
        abort(403, 'You are not authorized to perform this action')

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'message': 'Comment deleted successfully'}), 200

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.getenv('UPLOAD_FOLDER'), filename)

from flask_jwt_extended import jwt_required, get_jwt_identity

@bp.route('/get_posts', methods=['GET'])
@jwt_required()
def get_posts():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user:
        following_users = [follow.id for follow in user.following]  
        following_users.append(user.id)  

        posts = Post.query.filter(Post.user_id.in_(following_users)).all()

        post_data = []
        for post in posts:
            post_dict = {
                'id': post.id,
                'content': post.content,
                'image': post.image,
                'user_id': post.user_id,
                'likes': post.count_likes(),
                'comments': [comment.to_json() for comment in post.comments]
            }
            post_data.append(post_dict)

        followers_count = len(user.followers) 
        following_count = len(user.following)
        likes_received = user.count_likes_received()
        post_data.append({"followers_count": followers_count, "following_count": following_count, "likes_received": likes_received})

        return jsonify(post_data), 200
    else:
        return jsonify({'message': "You are not following any user"}), 404
