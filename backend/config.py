import os
from pathlib import Path

class Config:
    # Get the base directory of your project
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR / 'household_services.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for session management
    SECRET_KEY = 'your-secret-key-here'
