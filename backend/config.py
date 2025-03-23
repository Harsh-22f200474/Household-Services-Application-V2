import os
from datetime import timedelta
from pathlib import Path

class Config:
    # Get the base directory of your project
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR / 'household_services.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = 'your-jwt-secret-key'  # Change this to a secure secret key
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
