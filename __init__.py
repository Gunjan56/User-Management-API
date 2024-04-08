from flask import Flask
from app.config import Config
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail
from app.model import db


migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.main.apis.authentication import auth_bp
    app.register_blueprint(auth_bp)
    from app.main.apis.comment import comment_bp
    app.register_blueprint(comment_bp)
    from app.main.apis.follow import follow_bp
    app.register_blueprint(follow_bp)

    from app.main.apis.like import like_bp
    app.register_blueprint(like_bp)
    from app.main.apis.message import message_bp
    app.register_blueprint(message_bp)
    from app.main.apis.post import post_bp
    app.register_blueprint(post_bp)

    from app.main.apis.profile import profile_bp
    app.register_blueprint(profile_bp)

    from app.main.apis.search import search_bp
    app.register_blueprint(search_bp)

    from app.main.apis.handlers import handlers_bp
    app.register_blueprint(handlers_bp)

    return app
