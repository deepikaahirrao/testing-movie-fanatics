from flask import Blueprint, jsonify
from .movies import api_v1


welcome = Blueprint('welcome', __name__)


@welcome.route("/", methods=['GET'])
def welcome_page():
    return jsonify({"sucsess": True, "msg": 'Welcome to all movie fanatics'}), 200


def add_routes(app):
    app.register_blueprint(welcome)
    app.register_blueprint(api_v1)
