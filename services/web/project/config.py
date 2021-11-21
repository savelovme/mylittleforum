import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "very_secret"
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
