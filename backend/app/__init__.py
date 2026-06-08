from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from .config import Config
from .models import db

def create_app():
    
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    JWTManager(app)
    CORS(app, origins=["http://localhost:5173"])

    with app.app_context():
        db.create_all()

    from .auth import auth_bp
    from .logs import logs_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(logs_bp, url_prefix="/logs")

    @app.route('/health')
    def health():
        from flask import jsonify
        return jsonify({"status": "ok", "service": "symptomtrack-api"})
    
    return app


    