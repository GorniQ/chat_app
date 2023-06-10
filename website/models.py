import datetime
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_moderator = db.Column(db.Boolean, default=False)


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.relationship('Message', backref='chat', lazy=True)
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())

    sender = db.relationship('User', foreign_keys=[sender_id])


class Ban(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


class OnlineUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    last_seen = db.Column(db.DateTime(timezone=True), default=func.now())

# from . import db
# from flask_login import UserMixin
# from sqlalchemy.sql import func


# # ''' TODO: stworzenie klasy wiadomości (Message)
# #         - przemyśleć w jaki sposób przechowujemy widomości i jak bedziemy je odczytywac i wyświetlać
# #     TODO: stworzenie klasy czatu (ChatRoom)
# #     - zawiera w sobie id użytkowników piszących ze soba (user_id_1, user_id_2),
# #     - dziedziczy z klasy Message (db.relationship)??? jakies połącznie miedzy pokojem a wiadomościami,
# #     - port na jakim utworzony jest pokój???)
# #     TODO: dodanie klasy (Server)???
# #     - uruchomione czaty (porty do chatroomów)
# #     - aktywni/zalogowani użytkownicy
# #     TODO: przemyśleć jak zrobić tego moderatora
# # '''


# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     data = db.Column(db.String(10000))
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(150), unique=True)
#     password = db.Column(db.String(150))
#     first_name = db.Column(db.String(150))
#     notes = db.relationship('Note')
