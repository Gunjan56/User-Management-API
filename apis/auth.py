from email.message import Message
from flask import (request,jsonify, abort, g)
from flask_jwt_extended import (create_access_token, get_jwt_identity, jwt_required)
import base64 
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv, dotenv_values
from models.model import User, db
from __init__ import mail
load_dotenv()
import os
import re
from werkzeug.security import (check_password_hash, generate_password_hash)
from werkzeug.utils import (secure_filename)
from flask import Blueprint
from config import Config
email_validation = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'
bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(os.get('UPLOAD_FOLDER'), filename))
            data['profile_picture'] = filename

    if not re.match(email_validation, data.get('email')):
        return jsonify({'message': 'Enter a valid email'}), 400

    if not data.get('username') or not data.get('email') or not data.get('password'):
        abort(400, 'missing required details')

    user = User.query.filter_by(username=data.get('username'), email=data.get('email')).first()

    if user:
        return jsonify({'message': "User already registered"}), 400

    hashed_password = generate_password_hash(data.get('password'))

    new_user = User(
        username=data.get('username'),
        email=data.get('email'),
        password=hashed_password,
        profile_picture=data.get('profile_picture')
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data.get('username') or not data.get('password'):
        abort(400, 'Missing required details')

    user = User.query.filter_by(username=data.get('username')).first()

    if not user or not check_password_hash(user.password, data['password']):
        abort(401, 'Invalid username or password')

    access_token = create_access_token(identity=user.id)

    return jsonify(access_token=access_token), 200

@bp.route('/profile/picture', methods=['PUT'])
@jwt_required()
def update_profile_picture():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        abort(404, 'user not found')

    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(os.getenv('UPLOAD_FOLDER'), filename))
            user.profile_picture = filename
            db.session.commit()

            return jsonify({'message': 'Profile picture updated successfully'}), 200

    return jsonify({'error': 'No profile picture'}), 400

@bp.route('/profile', methods=['GET', 'PUT', 'DELETE'])
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
        if current_user_id.role != 'administrator':
            abort(403, 'You are not authorized')

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.role = data.get('role', user.role);
        
        if 'profile_picture' in request.files:
                profile_picture = request.files['profile_picture']
                if profile_picture and allowed_file(profile_picture.filename):
                    filename = secure_filename(profile_picture.filename)
                    profile_picture.save(os.path.join(os.getenv('UPLOAD_FOLDER'), filename))
                    user.profile_picture = filename

        db.session.commit()

        return jsonify({'message': 'User updated successfully'}), 200
        

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'User deleted successfully'}), 200

@bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def view_profile(user_id):
    user = User.query.get(user_id)

    if not user:
        abort(404, 'User not found')

    followers_count = user.count_followers()
    following_count = user.count_following()

    return jsonify({
        'username': user.username,
        'email': user.email,
        'profile_picture': user.profile_picture,
        'followers': followers_count,
        'following': following_count
    }), 200

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in os.getenv('ALLOWED_EXTENSIONS')

def secure_password(password):
    return generate_password_hash(password)    

@bp.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
   
    data = request.get_json()
    new_password = data['new_password']
    confirm_password = data['confirm_password']
    
    if new_password != confirm_password:
        return jsonify({'message': 'New password and confirm password do not match'}), 400

    email = base64.b64decode(token).decode('utf-8')
    
    user = User.query.filter_by(email=email).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'message': 'Password reset successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data['email']
    user = User.query.filter_by(email=email).first()
    
    if user:
        reset_token = base64.b64encode(email.encode('utf-8')).decode('utf-8')

        send_reset_password_email(email, reset_token)

        return jsonify({'message': 'Reset password link sent to your email'})
    else:
        return jsonify({'message': 'User not found'}), 404

def send_reset_password_email(user_email, reset_token):
    msg = Message('Reset Your Password', sender=os.getenv('MAIL_USERNAME'), recipients=[user_email])
    msg.body = f'Reset your password: {reset_token}'
    mail.send(msg)

