from flask import Blueprint

apis = Blueprint('apis', __name__)

from . import authentication, profile, post, follow, like, comment, message, search, handlers
