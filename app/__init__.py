from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024  # for example, to allow up to 16MB files
    from .routes import main
    app.register_blueprint(main)
    CORS(app)
    return app
