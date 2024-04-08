from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.model import db, User, Message
from app.main.validators.validators import Validators

message_bp = Blueprint('message', __name__)

@message_bp.route('/send_message/<int:recipient_id>', methods=['POST'])
@jwt_required()
def send_message(recipient_id):
    current_user_id = get_jwt_identity()

    validation_result = Validators.validate_user_id(recipient_id)
    if validation_result["status"] != 200:
        return jsonify(validation_result), validation_result["status"]

    sender = User.query.get(current_user_id)
    recipient = User.query.get(recipient_id)

    if not sender or not recipient:
        abort(404, 'Sender or recipient not found')

    data = request.json
    content = data.get('content')

    validation_result = Validators.validate_message_content(content)
    if validation_result["status"] != 200:
        return jsonify(validation_result), validation_result["status"]

    message = Message(
        sender_id=current_user_id,
        recipient_id=recipient_id,
        content=content
    )

    db.session.add(message)
    db.session.commit()

    return jsonify({'message': 'Message sent successfully'}), 201

@message_bp.route('/get_messages', methods=['GET'])
@jwt_required()
def get_messages():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        abort(404, 'User not found')

    sent_messages = Message.query.filter_by(sender_id=current_user_id).all()
    received_messages = Message.query.filter_by(recipient_id=current_user_id).all()

    sent_messages_data = [{'id': msg.id, 'sender_id': msg.sender_id, 'content': msg.content} for msg in sent_messages]
    received_messages_data = [{'id': msg.id, 'sender_id': msg.sender_id, 'content': msg.content} for msg in received_messages]

    return jsonify({'sent_messages': sent_messages_data, 'received_messages': received_messages_data}), 200

@message_bp.route('/delete_message/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    current_user_id = get_jwt_identity()
    message = Message.query.get(message_id)

    if not message:
        abort(404, 'Message not found')

    if message.sender_id != current_user_id and message.recipient_id != current_user_id:
        abort(403, 'You are not authorized to delete this message')

    db.session.delete(message)
    db.session.commit()
    return jsonify({'message': 'Message deleted successfully'}), 200
