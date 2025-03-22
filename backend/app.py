from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize Flask extensions
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
