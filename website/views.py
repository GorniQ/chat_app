from flask_socketio import join_room, emit
from sqlalchemy.orm import joinedload
from flask import Blueprint, jsonify, render_template, request, flash
from flask_login import login_required, current_user
from .models import Message, User, Chat, Ban, OnlineUser
from . import db, socketio
import json

views = Blueprint('views', __name__)


class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Message):
            return {
                'id': obj.id,
                'content': obj.content,
                'timestamp': obj.timestamp.strftime('%Y-%m-%d %H:%M'),
                'sender_id': obj.sender_id,
                'sender': {
                    'first_name': obj.sender.first_name,
                    'last_name': obj.sender.last_name
                }
            }
        return super().default(obj)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    chats = Chat.query.filter((Chat.user1_id == current_user.id) | (
        Chat.user2_id == current_user.id)).all()

    def is_user_online(user):
        online_user = OnlineUser.query.filter_by(user_id=user.id).first()
        return online_user is not None

    return render_template('home.html', user=current_user, chats=chats, is_user_online=is_user_online)


@views.route('/chats/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def chat(chat_id):
    chat = Chat.query.get(chat_id)
    if chat.user1_id == current_user.id:
        other_user = User.query.get(chat.user2_id)
    else:
        other_user = User.query.get(chat.user1_id)

    messages = Message.query.filter_by(chat_id=chat_id).options(
        joinedload(Message.sender)).all()

    return render_template("chats.html", chat=chat, other_user=other_user, user=current_user, messages=messages)


@socketio.on('join_chat')
def join_chat(data):
    chat_id = data['chatId']
    join_room(str(chat_id))


@socketio.on('send_message')
def send_message(data):
    chat_id = data['chatId']
    message_content = data['message']

    message = Message(
        chat_id=chat_id, sender_id=current_user.id, content=message_content)
    db.session.add(message)
    db.session.commit()

    # Retrieve the message with the sender information
    message_with_sender = Message.query.filter_by(
        id=message.id).join(User).first()

    emit('new_message', {
        'message': message_content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M'),
        'sender_id': current_user.id,
        'sender': {
            'first_name': current_user.first_name,
            'last_name': current_user.last_name
        }
    }, room=str(chat_id))


@views.route('/active', methods=['GET', 'POST'])
def active():
    users = User.query.all()

    def is_user_online(user):
        online_user = OnlineUser.query.filter_by(user_id=user.id).first()
        return online_user is not None

    return render_template('active.html', users=users, user=current_user, is_user_online=is_user_online)


@views.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template("settings.html", user=current_user)


@views.route('/manage', methods=['GET', 'POST'])
def manage():
    return render_template("manage.html", user=current_user)


@socketio.on('create_chat')
def create_chat(data):
    user2_id = data['userId']
    user1_id = current_user.id

    # Create a new chat room
    chat = Chat(user1_id=user1_id, user2_id=user2_id)
    db.session.add(chat)
    db.session.commit()

    # Join the chat room using SocketIO
    room = str(chat.id)
    join_room(room)

    # Redirect the user to the new chat room
    redirect_url = '/chats/' + room
    emit('redirect', {'url': redirect_url}, room=room)
