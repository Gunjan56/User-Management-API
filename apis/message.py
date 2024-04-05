from email.message import Message
from flask import (request,jsonify, abort)
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from dotenv import load_dotenv, dotenv_values
from models.model import User, db
load_dotenv()
from flask_socketio import SocketIO, emit
from flask import Blueprint
from config import Config
socketio = SocketIO()
bp = Blueprint('messages', __name__)

@bp.route('/send_message/<int:recipient_id>', methods=['POST'])
@jwt_required()
def send_message(recipient_id):
    current_user_id = get_jwt_identity()
    sender = User.query.get(current_user_id)
    recipient = User.query.get(recipient_id)

    if not sender or not recipient:
        abort(404, 'Sender or recipient not found')

    data = request.json
    content = data.get('content')

    if not content:
        abort(400, 'Content is required')

    message = Message(
        sender_id=current_user_id,
        recipient_id=recipient_id,
        content=content
    )

    db.session.add(message)
    db.session.commit()

    socketio.emit('new_message', {'sender_id': current_user_id, 'recipient_id': recipient_id, "content": content}, room=f'user_{recipient_id}')
    return jsonify({'message': 'Message sent successfully'}), 201

@socketio.on('message')
def handle_message(data):
    message = data.get('content')
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    current_user_id = get_jwt_identity()
    sender = User.query.get(sender_id)
    recipient = User.query.get(recipient_id)

    if not sender or not recipient:
        abort(404, 'Sender or recipient not found')

    message = Message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        content=message
    )
    db.session.add(message)
    db.session.commit()
    socketio.emit('new_message', {'sender_id': sender_id, 'recipient_id': recipient_id, "content": message}, room=f'user_{recipient_id}')
    print('Received message:', message)

def send_message(sender_id, recipient_id, content):
    emit('message', {'sender_id': sender_id, 'content': content}, room=f'user_{recipient_id}')
    socketio.emit('new_message', {'sender_id': sender_id, 'recipient_id': recipient_id, "content": content}, room=f'user_{recipient_id}')

@bp.route('/messages', methods=['GET'])
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

@bp.route('/delete_message/<int:message_id>', methods=['DELETE'])
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

