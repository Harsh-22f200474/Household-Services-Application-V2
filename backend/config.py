import os
from datetime import timedelta
from pathlib import Path

class Config:
    # Get the base directory of your project
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///household_services.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = '7a5f3d2c9e8b4f1a6d7e3c1b8a9f0d4e'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Flask configuration
    SECRET_KEY = 'd3c1b8a9e7f6d5c4b3a2f1e0d9c8b7a6'
    JSON_SORT_KEYS = False

    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'harshbadala0805@gmail.com')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'ezcclfdztlzoulzj')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'harshbadala0805@gmail.com')

    # Celery configuration
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True

    # Redis configuration
    REDIS_URL = 'redis://localhost:6379/0'
