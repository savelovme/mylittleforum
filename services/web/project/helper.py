from flask_sqlalchemy import SQLAlchemy
import json
import hashlib as hl
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    current_user,
)


def db_tables(app):

    db = SQLAlchemy(app)

    class Topic(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.Text)
        content = db.Column(db.Text)
        date = db.Column(db.Text)
        lastActivity = db.Column(db.Text)
        author = db.Column(db.Text)
        category = db.Column(db.Text)
        private = db.Column(db.Boolean)
        likes = db.Column(db.Text)
        replies = db.Column(db.Text)

        likesNum = db.Column(db.Integer)
        repliesNum = db.Column(db.Integer)
        views = db.Column(db.Integer)

        def __init__(self, title, content, date, author, category, private=False):
            self.title = title
            self.content = content
            self.date = date
            self.author = author
            self.category = category
            self.private = private
            self.likesNum = 0
            self.repliesNum = 0
            self.views = 0
            self.likes = "[]"
            self.lastActivity = date

        def like(self, username):
            l = json.loads(self.likes)
            if username in l:
                l.remove(username)
                self.likesNum -= 1
                self.likes = json.dumps(l)
            else:
                l.append(username)
                self.likesNum += 1
                self.likes = json.dumps(l)

        def reply(self, date):
            self.lastActivity = date
            self.repliesNum += 1

    class Reply(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.Text)
        date = db.Column(db.Text)
        author = db.Column(db.Text)
        inReplyTo = db.Column(db.Integer)
        likes = db.Column(db.Text)

        likesNum = db.Column(db.Integer)

        def __init__(self, content, date, author, inReplyTo):
            self.content = content
            self.date = date
            self.author = author
            self.inReplyTo = inReplyTo
            self.likesNum = 0
            self.likes = "[]"

        def like(self, username):
            l = json.loads(self.likes)
            if username in l:
                l.remove(username)
                self.likesNum -= 1
                self.likes = json.dumps(l)
            else:
                l.append(username)
                self.likesNum += 1
                self.likes = json.dumps(l)

    return db, Topic, Reply

def initLogin(app, db):
    # Create the User clasis
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.Text, unique=True)
        password = db.Column(db.Text)

        def __init__(self, username, password):
            self.username = username
            self.password = password

    # Configure login
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return User


def loginUser(username, password, User):
    # Hash the username and the password
    # username = hl.md5(bytes(username, 'utf-8')).hexdigest()
    password = hl.md5(bytes(password, "utf-8")).hexdigest()

    # Check if it exists
    user = User.query.filter_by(username=username, password=password).first_or_404()
    login_user(user)
    return True


def createUser(username, password, db, User):
    # hash the username and the password
    # username = hl.md5(bytes(username, 'utf-8')).hexdigest() # Comment this is you want a clear username
    password = hl.md5(bytes(password, "utf-8")).hexdigest()

    # Send them to db
    user = User(username, password)
    db.session.add(user)
    db.session.commit()

    # Login the user
    login_user(user)

    # return success
    return True


def get_Username():
    return current_user.username


# To restrict a page to a user just add @login_required
# To logout just do logout_user()
# To get the current username do current_user.username

