from socket import SocketIO
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from apis.utils.handlers import bad_request, forbidden, not_found, unauthorized
from apis.utils import decorator, handlers, helper
from config import Config
from models.model import db


jwt = JWTManager()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.errorhandler(400)(bad_request)
    app.errorhandler(401)(unauthorized)
    app.errorhandler(403)(forbidden)
    app.errorhandler(404)(not_found)
    app.config.from_object(Config)
    migrate.init_app(app, db)
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)


    from apis import auth, follow, posts, message, search, handlers

    app.register_blueprint(auth.bp)
    app.register_blueprint(follow.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(message.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(handlers.bp)
    return app
