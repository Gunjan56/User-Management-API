from flask import (request,jsonify, abort, g)
from dotenv import load_dotenv, dotenv_values
from models.model import User, db, Post
load_dotenv()
from flask import Blueprint
from config import Config

bp = Blueprint('search', __name__)

@bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    search_type = request.args.get('type')  

    if not query or not search_type:
        abort(400, 'Query and search type are required')

    if search_type == 'posts':
        posts = Post.query.filter(Post.content.like(f'%{query}%')).all()
        search_results = [post.to_json() for post in posts]

    elif search_type == 'users':
        users = User.query.filter(
            (User.username.ilike(f'%{query}%')) | (User.email.ilike(f'%{query}%'))
        ).all()
        search_results = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]

    elif search_type == 'hashtags':
        posts = Post.query.filter(Post.content.ilike(f'%#{query}%')).all()
        search_results = [post.to_json() for post in posts]

    else:
        abort(400, 'Invalid search type')

    sort_by = request.args.get('sort_by')
    if sort_by:
        if sort_by == 'likes':
            search_results.sort(key=lambda x: len(x['likes']), reverse=True)
        else:
            abort(400, 'Invalid sort_by parameter')

    return jsonify({'results': search_results}), 200

