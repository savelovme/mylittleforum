# This is only a module to make the login process faster and easier. Don't care about it unless you also wants a simple login for your app
import hashlib as hl
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    current_user,
)


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
