# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize CSRFProtect
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')

    # Initialize extensions with the app
    db.init_app(app)
    csrf.init_app(app)

    # Make csrf_token available in all templates
    @app.context_processor
    def utility_processor():
        def csrf_token():
            return generate_csrf()
        return dict(csrf_token=csrf_token)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.blog import blog_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)

    # Create database tables within app context
    with app.app_context():
        db.create_all()

    return app