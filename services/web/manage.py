from flask.cli import FlaskGroup
from project import db, create_app

cli = FlaskGroup(create_app=create_app)


@cli.command("create_db")
def create_db():
    #db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == "__main__":
    cli()
