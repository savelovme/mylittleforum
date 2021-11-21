import time
import os
from flask import Blueprint, render_template, redirect, request
from flask_login import login_required, current_user
from .config import Config
from .db_models import User, Topic, Reply
from . import db
from .model import frustration_model

main = Blueprint('main', __name__)


def get_time():
    return time.asctime(time.localtime(time.time()))  # Get the current time and date


def get_user(id):
    return User.query.filter_by(id=id).first_or_404()


@main.route('/')
@main.route('/index')
def index():
    topics = Topic.query.order_by(Topic.id.desc())
    return render_template('index.html', topics=topics, get_user=get_user)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, avatar=current_user.avatar)


@main.route('/profile', methods=['POST'])
@login_required
def upload_file():
    uploaded_file = request.files['file']
    _, file_ext = os.path.splitext(uploaded_file.filename)
    filename = 'avatars/' + str(current_user.id) + file_ext
    uploaded_file.save(os.path.join(Config.STATIC_FOLDER, filename))
    current_user.avatar = filename
    db.session.add(current_user)
    db.session.commit()
    return redirect("/profile")


@main.route("/post")  # Render the 'write new topic' box
@login_required
def renderCreateTopic():
    return render_template("post.html")


@main.route("/post/post", methods=["POST"])  # Backend of the new topic box
def createTopic():
    topic = Topic(
        request.form["title"],
        request.form["content"],
        get_time(),
        current_user.id,
        request.form["category"],
        frustration_model.predict_probas([request.form["content"]])[0,0].item()
    )
    db.session.add(topic)
    db.session.commit()
    return redirect("/topic/" + str(topic.id))


@main.route("/topic/<id>")  # Render a topic
def renderTopic(id):
    topic = Topic.query.filter_by(id=id).first_or_404()
    topic.views += 1  # Add one view
    db.session.add(topic)
    db.session.commit()  # Change the value of the view in the database
    return render_template(
        "topic.html", topic=topic, replies=Reply.query.filter_by(topic_id=id).order_by(Reply.id),
        get_user=get_user, test_score=topic.frustration
    )  # Render the page


@main.route("/reply/<id>", methods=["POST"])  # Reply to a post.
@login_required
def replyTo(id):
    topic = Topic.query.filter_by(id=id).first_or_404()
    topic.reply(get_time())  # Reply to the topic
    reply = Reply(
        request.form["body"], get_time(), current_user.id, id,
        frustration_model.predict_probas([request.form["body"]])[0, 0].item()
    )  # Add the reply
    db.session.add(reply)
    db.session.add(topic)
    db.session.commit()  # Add everything in the database
    return redirect("/topic/" + str(id))  # Redirect to the correct page


@main.route("/like/<id>")  # Like a topic
@login_required
def likeTopic(id):
    topic = Topic.query.filter_by(id=id).first_or_404()
    topic.like(current_user.id)  # Call the 'like' function of the class 'Topic'
    db.session.add(topic)
    db.session.commit()
    return redirect("/topic/" + str(id))


@main.route("/like/reply/<id>/<topic_id>")  # Like a reply
@login_required
def likeReply(id, topic_id):
    reply = Reply.query.filter_by(id=id).first_or_404()
    reply.like(current_user.id)  # Call the like function of the class Reply
    db.session.add(reply)
    db.session.commit()
    return redirect("/topic/" + str(topic_id))  # Return to the topic


@main.route("/top")  # Order the list of posts by thoses who have the biggest number of replies
def topList():
    topics = Topic.query.order_by(Topic.repliesNum.desc())
    return render_template("index.html", topics=topics, get_user=get_user)


@main.route("/new")  # Order the list like normal (redirect)
def redirectIndex():
    return redirect("/")


@main.route("/cat/<category>")  # Get the list of posts in a category
def catList(category):
    topics = Topic.query.filter_by(category=category).order_by(Topic.id.desc())
    return render_template("index.html", topics=topics, get_user=get_user)

