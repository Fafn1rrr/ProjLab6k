"""Drukāšanas pasūtījumu izpildes plānošana — Flask lietotnes izveide."""
import os
import sys

from dotenv import load_dotenv
from flask import Flask, render_template
from sqlalchemy.exc import OperationalError, ProgrammingError

from .models import db


def create_app():
    # Windows konsole (cp1251/cp1252) nevar izvadīt latviešu burtus un krīt ar UnicodeEncodeError.
    # Neizvadāmos simbolus aizstājam ar «?», nevis apturam programmu.
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(errors="replace")

    load_dotenv()  # nolasa .env failu
    app = Flask(__name__)
    if not os.environ.get("DATABASE_URL"):
        raise RuntimeError("Nav norādīts DATABASE_URL. Nokopējiet .env.example kā .env (sk. README).")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
    app.json.ensure_ascii = False  # latviešu burti JSON atbildēs bez \u kodiem
    db.init_app(app)

    from .cli import register_cli
    from .routes import bp

    app.register_blueprint(bp)
    register_cli(app)

    @app.errorhandler(OperationalError)
    @app.errorhandler(ProgrammingError)
    def database_error(err):
        # Nav savienojuma ar DB vai nav tabulu — parādām instrukciju, nevis kļūdas tekstu.
        db.session.rollback()
        return render_template("db_error.html", error=str(err.orig or err)), 500

    return app
