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
    return time.strftime("%d %b %Y %H:%M:%S" , time.localtime(time.time()))

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
    frustration_stat = dict()
    frustration_stat["frustrated_topics"] = Topic.query.filter(Topic.author_id == current_user.id,
                                                               Topic.frustration > 0.5).count()
    frustration_stat["total_topics"] = Topic.query.filter(Topic.author_id == current_user.id).count()
    frustration_stat["frustrated_replies"] = Reply.query.filter(Reply.author_id == current_user.id,
                                                               Reply.frustration > 0.5).count()
    frustration_stat["total_replies"] = Reply.query.filter(Reply.author_id == current_user.id).count()

    return render_template('profile.html', name=current_user.name, avatar=current_user.avatar, frustration_stat=frustration_stat)


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


@main.route("/post")
@login_required
def renderCreateTopic():
    return render_template("post.html")


@main.route("/post/post", methods=["POST"])
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


@main.route("/topic/<id>")
def renderTopic(id):
    topic = Topic.query.filter_by(id=id).first_or_404()
    topic.views += 1
    db.session.add(topic)
    db.session.commit()
    return render_template(
        "topic.html", topic=topic, replies=Reply.query.filter_by(topic_id=id).order_by(Reply.id), get_user=get_user
    )


@main.route("/reply/<id>", methods=["POST"])
@login_required
def replyTo(id):
    topic = Topic.query.filter_by(id=id).first_or_404()
    topic.reply(get_time())
    reply = Reply(
        request.form["body"], get_time(), current_user.id, id,
        frustration_model.predict_probas([request.form["body"]])[0, 0].item()
    )
    db.session.add(reply)
    db.session.add(topic)
    db.session.commit()
    return redirect("/topic/" + str(id))


@main.route("/like/<id>")
@login_required
def likeTopic(id):
    topic = Topic.query.filter_by(id=id).first_or_404()
    topic.like(current_user.id)
    db.session.add(topic)
    db.session.commit()
    return redirect("/topic/" + str(id))


@main.route("/like/reply/<id>/<topic_id>")
@login_required
def likeReply(id, topic_id):
    reply = Reply.query.filter_by(id=id).first_or_404()
    reply.like(current_user.id)
    db.session.add(reply)
    db.session.commit()
    return redirect("/topic/" + str(topic_id))


@main.route("/top")
def topList():
    topics = Topic.query.order_by(Topic.repliesNum.desc())
    return render_template("index.html", topics=topics, get_user=get_user)


@main.route("/new")
def redirectIndex():
    return redirect("/")


@main.route("/cat/<category>")
def catList(category):
    topics = Topic.query.filter_by(category=category).order_by(Topic.id.desc())
    return render_template("index.html", topics=topics, get_user=get_user)

