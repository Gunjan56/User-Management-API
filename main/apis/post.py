from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.model import db, User, Post
from app.main.validators.validators import Validators

post_bp = Blueprint('post', __name__)

@post_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        abort(404, 'User not found')

    data = request.json
    content = data.get('content')

    validation_result = Validators.validate_post_content(content)
    if validation_result["status"] != 200:
        return jsonify(validation_result), validation_result["status"]

    new_post = Post(
        content=content,
        user_id=current_user_id
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created successfully'}), 201

@post_bp.route('/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
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
        abort(403, 'You are not authorized to perform this action')

    if request.method == 'GET':
        return jsonify({
            'id': post.id,
            'content': post.content
        }), 200

    elif request.method == 'PUT':
        data = request.json

        content = data.get('content', post.content)

        validation_result = Validators.validate_post_content(content)
        if validation_result["status"] != 200:
            return jsonify(validation_result), validation_result["status"]

        post.content = content
        db.session.commit()

        return jsonify({'message': 'Post updated successfully'}), 200

@post_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    current_user_id = get_jwt_identity()
    post = Post.query.get(post_id)

    if not post:
        abort(404, 'Post not found')

    if post.user_id != current_user_id:
        abort(403, 'You are not authorized to delete this post')

    db.session.delete(post)
    db.session.commit()

    return jsonify({'message': 'Post deleted successfully'}), 200

@post_bp.route('/get_posts', methods=['GET'])
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