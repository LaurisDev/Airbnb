from flask import Flask
from app.routes import init_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = 'clave_secreta_segura'  # para poder usar flash messages
    init_routes(app)
    return app