from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from app.model import db, User
from app.main.validators.validators import Validators
from app.utils import allowed_file
from flask_mail import Message, Mail
import os
import base64
from werkzeug.utils import secure_filename

mail = Mail()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    validation_result = Validators.check_user_required_fields(data)
    if validation_result["status"] == 200:
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture and allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(os.getenv('UPLOAD_FOLDER'), filename))
                data['profile_picture'] = filename

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
    else:
        return jsonify(validation_result), validation_result["status"]

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    validation_result = Validators.check_login_required_fields(data)
    if validation_result["status"] == 200:
        user = User.query.filter_by(username=data.get('username')).first()

        if not user or not check_password_hash(user.password, data['password']):
            abort(401, 'Invalid username or password')

        access_token = create_access_token(identity=user.id)

        return jsonify(access_token=access_token), 200
    else:
        return jsonify(validation_result), validation_result["status"]

@auth_bp.route('/forgot_password', methods=['POST'])
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

@auth_bp.route('/reset_password/<token>', methods=['POST'])
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
