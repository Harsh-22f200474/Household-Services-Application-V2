from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from config import Config
from extensions import db, jwt, bcrypt, cors
from flask_cors import CORS
from datetime import datetime
import json

def create_app():
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Load configuration
    app.config.from_object(Config)
    
    # Configure a custom JSON provider to handle datetime objects
    class CustomJSONProvider(DefaultJSONProvider):
        def dumps(self, obj, **kwargs):
            return json.dumps(obj, default=self.default, **kwargs)

        def loads(self, s, **kwargs):
            return json.loads(s, **kwargs)

        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)
    
    # Set the custom JSON provider (remove legacy json_encoder assignment)
    app.json_provider_class = CustomJSONProvider

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    
    # Root route
    @app.route('/')
    def home():
        return jsonify({
            "message": "Welcome to Household Services API",
            "status": "running"
        })
    
    # Register blueprints
    with app.app_context():
        from routes.auth import auth_bp
        from routes.admin import admin_bp
        from routes.professional import professional_bp
        from routes.customer import customer_bp
        from routes.services import services_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(professional_bp, url_prefix='/api/professional')
        app.register_blueprint(customer_bp, url_prefix='/api/customer')
        app.register_blueprint(services_bp, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not Found'}), 404

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({'error': 'Unauthorized'}), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({'error': 'Forbidden'}), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)