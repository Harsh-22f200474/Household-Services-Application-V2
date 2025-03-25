from app import create_app
from extensions import db
from models.models import User, Professional, Service
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

def setup_test_data():
    app = create_app()
    with app.app_context():
        # Load environment variables
        load_dotenv()
        
        # Create test services if they don't exist
        services = {
            'House Cleaning': Service(
                name='House Cleaning',
                description='Complete house cleaning service',
                base_price=100,
                time_required=120,
                is_active=True
            ),
            'Plumbing': Service(
                name='Plumbing',
                description='Professional plumbing services',
                base_price=150,
                time_required=60,
                is_active=True
            ),
            'Electrical': Service(
                name='Electrical',
                description='Electrical repair and installation',
                base_price=200,
                time_required=90,
                is_active=True
            )
        }
        
        for service_name, service in services.items():
            existing_service = Service.query.filter_by(name=service_name).first()
            if not existing_service:
                db.session.add(service)
        
        # Create test professionals with Google Chat webhooks
        professionals = [
            {
                'username': 'cleaner1',
                'email': 'cleaner1@example.com',
                'name': 'John Cleaner',
                'service_type': 'House Cleaning',
                'chat_webhook': 'https://chat.googleapis.com/v1/spaces/AAAAvRakfdA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=553wVqWmLUKCOHrlADdcoxnF4ThoR0MznD1WqQn3m18'  # Replace with your actual webhook URL
            },
            {
                'username': 'plumber1',
                'email': 'plumber1@example.com',
                'name': 'Mike Plumber',
                'service_type': 'Plumbing',
                'chat_webhook': 'https://chat.googleapis.com/v1/spaces/AAAAvRakfdA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=553wVqWmLUKCOHrlADdcoxnF4ThoR0MznD1WqQn3m18'  # Replace with your actual webhook URL
            },
            {
                'username': 'electrician1',
                'email': 'electrician1@example.com',
                'name': 'Tom Electrician',
                'service_type': 'Electrical',
                'chat_webhook': 'https://chat.googleapis.com/v1/spaces/AAAAvRakfdA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=553wVqWmLUKCOHrlADdcoxnF4ThoR0MznD1WqQn3m18'  # Replace with your actual webhook URL
            }
        ]
        
        for prof_data in professionals:
            # Check if professional exists
            existing_user = User.query.filter_by(username=prof_data['username']).first()
            if not existing_user:
                # Create new professional
                service = Service.query.filter_by(name=prof_data['service_type']).first()
                if service:
                    user = User(
                        username=prof_data['username'],
                        email=prof_data['email'],
                        name=prof_data['name'],
                        role='professional',
                        password_hash=generate_password_hash('default_password').encode('utf-8'),  # Set a default password
                        chat_webhook_url=prof_data['chat_webhook']
                    )
                    db.session.add(user)
                    db.session.flush()
                    
                    professional = Professional(
                        user_id=user.id,
                        service_type=prof_data['service_type'],
                        experience=5,
                        description=f'Experienced {prof_data["service_type"].lower()} professional',
                        is_verified=True
                    )
                    db.session.add(professional)
        
        try:
            db.session.commit()
            print("Test data setup completed successfully!")
        except Exception as e:
            print(f"Error setting up test data: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    setup_test_data() 