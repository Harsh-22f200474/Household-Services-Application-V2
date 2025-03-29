from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, CustomerProfile, ProfessionalProfile, Service, ServiceRequest, Review

def populate_database():
    print("Clearing existing data...")
    # Clear existing data
    try:
        Review.query.delete()  # Delete reviews first due to foreign key constraints
        ServiceRequest.query.delete()
        Service.query.delete()
        ProfessionalProfile.query.delete()
        CustomerProfile.query.delete()
        User.query.delete()
        db.session.commit()
    except Exception as e:
        print(f"Error clearing data: {e}")
        db.session.rollback()

    print("Creating admin user...")
    # Create admin user
    admin = User(
        username="admin",
        password=generate_password_hash("admin123"),
        role="Admin",
        approve=True,  # Admin is always approved
        blocked=False  # Admin is never blocked
    )
    db.session.add(admin)

    # Create service types and their corresponding services
    service_types = [
        {
            "type": "Cleaning",
            "services": ["House Cleaning", "Office Cleaning", "Deep Cleaning", "Window Cleaning"]
        },
        {
            "type": "Plumbing",
            "services": ["Pipe Repair", "Drain Cleaning", "Fixture Installation", "Water Heater Service"]
        },
        {
            "type": "Electrical",
            "services": ["Wiring Installation", "Light Fixture Setup", "Circuit Repair", "Safety Inspection"]
        },
        {
            "type": "Carpentry",
            "services": ["Furniture Assembly", "Cabinet Installation", "Wood Repair", "Custom Woodwork"]
        }
    ]

    print("Creating services...")
    # Create services
    services = []
    for service_category in service_types:
        for service_name in service_category["services"]:
            service = Service(
                name=service_name,
                description=f"Professional {service_category['type']} service - {service_name}",
                price=random.randint(500, 5000),
                service_type=service_category['type']
            )
            db.session.add(service)
            services.append(service)

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error committing services: {e}")
        db.session.rollback()
        return

    print("Creating professionals...")
    # Create professionals (2-4 per service type)
    professional_profiles = []
    for service_category in service_types:
        num_professionals = random.randint(2, 4)
        for i in range(num_professionals):
            # Create professional user with appropriate approval status
            # Make some professionals pre-approved for testing, others pending approval
            is_approved = random.choice([True, False])
            professional = User(
                username=f"{service_category['type'].lower()}_pro_{i+1}",
                password=generate_password_hash("password123"),
                role="Professional",
                approve=is_approved,  # Some professionals pre-approved for testing
                blocked=not is_approved  # Blocked if not approved
            )
            db.session.add(professional)
            db.session.flush()  # Get the ID

            # Create professional profile
            profile = ProfessionalProfile(
                user_id=professional.id,
                full_name=f"{service_category['type']} Professional {i+1}",
                service_type=service_category['type'],  # Using the service type string
                experience=f"{random.randint(1, 15)} years",
                filename="default.pdf",
                address=f"{random.randint(1, 999)} Professional Street, City",
                pin_code=str(random.randint(100000, 999999)),
                reviews=round(random.uniform(3.5, 5.0), 1)
            )
            db.session.add(profile)
            professional_profiles.append((professional, profile))

    print("Creating customers...")
    # Create customers (20-30)
    customers = []
    num_customers = random.randint(20, 30)
    for i in range(num_customers):
        # Create customer user (automatically approved, never blocked)
        customer = User(
            username=f"customer_{i+1}",
            password=generate_password_hash("password123"),
            role="Customer",
            approve=True,   # Customers are automatically approved
            blocked=False   # Customers start unblocked
        )
        db.session.add(customer)
        db.session.flush()

        # Create customer profile
        profile = CustomerProfile(
            user_id=customer.id,
            full_name=f"Customer {i+1}",
            address=f"{random.randint(1, 999)} Customer Avenue, City",
            pin_code=str(random.randint(100000, 999999))
        )
        db.session.add(profile)
        customers.append(customer)

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error committing users: {e}")
        db.session.rollback()
        return

    print("Creating service requests and reviews...")
    # Create service requests
    statuses = ['requested', 'accepted', 'rejected', 'completed']
    current_date = datetime.now()

    # Sample review comments
    positive_comments = [
        "Excellent service! Very professional and punctual.",
        "Great work, would definitely recommend!",
        "Very skilled and efficient. Clean work.",
        "Professional and courteous service.",
        "Outstanding job! Exceeded expectations."
    ]
    
    neutral_comments = [
        "Service was okay, got the job done.",
        "Decent work but took longer than expected.",
        "Average service, room for improvement.",
        "Satisfactory work but communication could be better.",
        "Met basic expectations."
    ]
    
    negative_comments = [
        "Service could have been better.",
        "Not very professional, needs improvement.",
        "Delayed and poor communication.",
        "Wouldn't recommend, below expectations.",
        "Disappointing service quality."
    ]

    # Create 50-100 service requests
    num_requests = random.randint(50, 100)
    for i in range(num_requests):
        # Random dates within the last 6 months
        request_date = current_date - timedelta(days=random.randint(0, 180))
        service_status = random.choice(statuses)
        
        # Select random service and professional that matches the service type
        service = random.choice(services)
        matching_professionals = [
            (p, profile) for p, profile in professional_profiles 
            if profile.service_type == service.service_type and p.approve  # Only approved professionals
        ]
        
        if not matching_professionals:
            continue  # Skip if no matching professionals
            
        professional, prof_profile = random.choice(matching_professionals)
        customer = random.choice(customers)
        
        service_request = ServiceRequest(
            service_id=service.id,
            customer_id=customer.id,
            professional_id=professional.id,
            remarks=f"Service request for {service.name}",
            service_status=service_status,
            date_of_request=request_date
        )

        # Add status-specific dates
        if service_status in ['accepted', 'rejected']:
            service_request.date_of_accept_reject = request_date + timedelta(days=random.randint(1, 3))
        
        if service_status == 'completed':
            service_request.date_of_accept_reject = request_date + timedelta(days=random.randint(1, 3))
            service_request.date_of_completion = service_request.date_of_accept_reject + timedelta(days=random.randint(1, 7))

        db.session.add(service_request)
        db.session.flush()  # Get the ID

        # Add review for completed services (80% chance of review)
        if service_status == 'completed' and random.random() < 0.8:
            rating = random.choices([5, 4, 3, 2, 1], weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]
            
            # Select appropriate comment pool based on rating
            if rating >= 4:
                comment = random.choice(positive_comments)
            elif rating == 3:
                comment = random.choice(neutral_comments)
            else:
                comment = random.choice(negative_comments)

            review = Review(
                service_request_id=service_request.id,
                customer_id=customer.id,
                professional_id=professional.id,
                rating=rating,
                comment=comment,
                created_at=service_request.date_of_completion + timedelta(days=random.randint(1, 5))
            )
            db.session.add(review)

            # Update professional's average rating
            prof_profile.update_average_rating()

    try:
        db.session.commit()
        print("Database populated successfully!")
    except Exception as e:
        print(f"Error committing service requests and reviews: {e}")
        db.session.rollback()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        populate_database()
