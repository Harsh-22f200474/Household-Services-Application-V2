from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from flask_caching import Cache
from flask_mail import Mail

from config import Config
from models import db
from utils.celery_tasks import init_celery
from routes.auth import auth_bp
from routes.file import file_bp
from routes.customer import customer_bp
from routes.professional import professional_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Set up static file handling
    app.static_folder = '../frontend/static'
    app.static_url_path = '/static'
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    swagger = Swagger(app)
    cache = Cache(app)
    mail = Mail(app)
    
    # Initialize Celery
    celery = init_celery(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(professional_bp)
    app.register_blueprint(admin_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Add root route
    @app.route('/')
    def index():
        """
        Serve the frontend index.html file
        """
        return send_from_directory('../frontend', 'index.html')
    
    # Serve frontend JavaScript files
    @app.route('/components/<path:filename>')
    def serve_component(filename):
        return send_from_directory('../frontend/components', filename)
    
    @app.route('/utils/<path:filename>')
    def serve_util(filename):
        return send_from_directory('../frontend/utils', filename)
    
    @app.route('/pages/<path:filename>')
    def serve_page(filename):
        return send_from_directory('../frontend/pages', filename)
    
    # Add API documentation route
    @app.route('/api')
    def api_docs():
        """
        Root endpoint that lists all available endpoints
        """
        return jsonify({
            "message": "Welcome to the Service Provider API",
            "available_endpoints": {
                "auth": ["/register", "/login", "/logout"],
                "customer": ["/customer/profile", "/customer/services", "/customer/professionals/<service_type>", "/customer/request", "/customer/requests"],
                "professional": ["/professional/profile", "/professional/requests", "/professional/request/<request_id>"],
                "admin": ["/admin/service", "/admin/service/<service_id>", "/admin/professionals", "/admin/professional/<user_id>/approve", "/admin/professional/<user_id>/block"],
                "files": ["/download/<filename>"]
            },
            "documentation": "/apidocs"  # Swagger documentation URL
        })
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)