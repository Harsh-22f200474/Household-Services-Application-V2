from app import create_app
from extensions import db
from models.models import User, Service, ServiceRequest
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

def create_test_requests():
    app = create_app()
    with app.app_context():
        # Get all services
        services = Service.query.all()
        if not services:
            print("No services found. Please run setup_test_data.py first.")
            return

        # Get all professionals
        professionals = User.query.filter_by(role='professional').all()
        if not professionals:
            print("No professionals found. Please run setup_test_data.py first.")
            return

        # Create test customers if they don't exist
        customers = [
            {
                'username': 'customer1',
                'email': 'customer1@example.com',
                'name': 'Alice Customer',
                'address': '123 Main St, City'
            },
            {
                'username': 'customer2',
                'email': 'customer2@example.com',
                'name': 'Bob Customer',
                'address': '456 Oak Ave, Town'
            }
        ]

        for customer_data in customers:
            existing_customer = User.query.filter_by(username=customer_data['username']).first()
            if not existing_customer:
                customer = User(
                    username=customer_data['username'],
                    email=customer_data['email'],
                    name=customer_data['name'],
                    role='customer',
                    password_hash=generate_password_hash('default_password').encode('utf-8'),  # Set a default password
                )
                db.session.add(customer)
                db.session.flush()

        # Create test service requests
        statuses = ['requested', 'assigned', 'completed']
        for _ in range(10):  # Create 10 test requests
            service = random.choice(services)
            customer = User.query.filter_by(role='customer').first()
            professional = random.choice(professionals)
            
            # Random date within the last 30 days
            days_ago = random.randint(0, 30)
            requested_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Random status
            status = random.choice(statuses)
            
            # Set completion date if status is completed
            completion_date = None
            if status == 'completed':
                completion_date = requested_date + timedelta(hours=random.randint(1, 8))
            
            request = ServiceRequest(
                customer_id=customer.id,
                service_id=service.id,
                professional_id=professional.id if status != 'requested' else None,
                status=status,
                requested_date=requested_date,
                scheduled_date=requested_date + timedelta(hours=random.randint(1, 24)),
                completion_date=completion_date,
                price=service.base_price,
                address=customer.customer_profile[0].address if customer.customer_profile else '123 Test St',  # Updated line
                notes='Test service request'
            )
            db.session.add(request)

        try:
            db.session.commit()
            print("Test service requests created successfully!")
        except Exception as e:
            print(f"Error creating test requests: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_requests() 