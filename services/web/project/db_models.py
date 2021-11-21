import json
from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    avatar = db.Column(db.String(1000))


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    date = db.Column(db.Text)
    lastActivity = db.Column(db.Text)
    author_id = db.Column(db.Integer)
    category = db.Column(db.Text)
    private = db.Column(db.Boolean)
    likes = db.Column(db.Text)
    replies = db.Column(db.Text)
    frustration = db.Column(db.Float)

    likesNum = db.Column(db.Integer)
    repliesNum = db.Column(db.Integer)
    views = db.Column(db.Integer)

    def __init__(self, title, content, date, author_id, category, frustration, private=False):
        self.title = title
        self.content = content
        self.date = date
        self.author_id = author_id
        self.category = category
        self.private = private
        self.likesNum = 0
        self.repliesNum = 0
        self.views = 0
        self.likes = "[]"
        self.lastActivity = date
        self.frustration = frustration

    def like(self, user_id):
        l = json.loads(self.likes)
        if user_id in l:
            l.remove(user_id)
            self.likesNum -= 1
            self.likes = json.dumps(l)
        else:
            l.append(user_id)
            self.likesNum += 1
            self.likes = json.dumps(l)

    def reply(self, date):
        self.lastActivity = date
        self.repliesNum += 1


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    date = db.Column(db.Text)
    author_id = db.Column(db.Integer)
    topic_id = db.Column(db.Integer)
    likes = db.Column(db.Text)
    frustration = db.Column(db.Float)

    likesNum = db.Column(db.Integer)

    def __init__(self, content, date, author_id, topic_id, frustration):
        self.content = content
        self.date = date
        self.author_id = author_id
        self.topic_id = topic_id
        self.likesNum = 0
        self.likes = "[]"
        self.frustration = frustration

    def like(self, user_id):
        l = json.loads(self.likes)
        if user_id in l:
            l.remove(user_id)
            self.likesNum -= 1
            self.likes = json.dumps(l)
        else:
            l.append(user_id)
            self.likesNum += 1
            self.likes = json.dumps(l)
