from app import create_app
from extensions import db, bcrypt
from models.models import User, Service, Professional, Customer, ServiceRequest
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def generate_professionals():
    """Generate professionals for each service."""
    service_types = Service.query.all()
    professionals = []
    
    for service in service_types:
        for _ in range(random.randint(4, 5)):  # 4-5 professionals per service
            professional = User(
                username=f"pro_{fake.unique.first_name().lower()}_{random.randint(100, 999)}",
                email=fake.unique.email(),
                password_hash=bcrypt.generate_password_hash('pro123').decode('utf-8'),
                name=fake.name(),
                role='professional',
                service_type_id=service.id
            )
            db.session.add(professional)
            db.session.flush()  # Get ID before committing
            
            professional_profile = Professional(
                user_id=professional.id,
                service_type=service.name,
                experience=random.randint(1, 15),  # 1-15 years of experience
                description=f"Experienced {service.name.lower()} professional",
                is_verified=random.choice([True, False])
            )
            db.session.add(professional_profile)
            professionals.append(professional)

    return professionals


def generate_customers():
    """Generate 40-50 customers with different attributes."""
    customers = []
    
    for _ in range(random.randint(40, 50)):  # 40-50 customers
        customer = User(
            username=f"cust_{random.randint(1000, 9999)}",
            email=fake.unique.email(),
            password_hash=bcrypt.generate_password_hash('cust123').decode('utf-8'),
            name=fake.name(),
            role='customer'
        )
        db.session.add(customer)
        db.session.flush()

        customer_profile = Customer(
            user_id=customer.id,
            address=fake.address(),
            phone=fake.phone_number()
        )
        db.session.add(customer_profile)
        customers.append(customer)
    
    return customers


def generate_service_requests(customers, professionals, services):
    """Generate random service requests with different statuses."""
    statuses = ["requested", "assigned", "completed", "cancelled", "rejected"]
    
    for _ in range(random.randint(50, 70)):  # 50-70 service requests
        customer = random.choice(customers)
        service = random.choice(services)
        professional = random.choice(professionals) if random.random() > 0.3 else None  # Some requests may not have professionals assigned

        requested_date = fake.date_time_between(start_date="-30d", end_date="now")
        scheduled_date = requested_date + timedelta(days=random.randint(1, 5)) if professional else None
        completion_date = scheduled_date + timedelta(days=random.randint(1, 5)) if scheduled_date and random.random() > 0.7 else None

        status = random.choice(statuses)
        if status == "completed" and completion_date is None:
            completion_date = scheduled_date + timedelta(days=random.randint(1, 3)) if scheduled_date else None

        service_request = ServiceRequest(
            customer_id=customer.id,
            service_id=service.id,
            professional_id=professional.id if professional else None,
            status=status,
            requested_date=requested_date,
            scheduled_date=scheduled_date,
            completion_date=completion_date,
            customer_rating=random.randint(1, 5) if status == "completed" else None,
            customer_review=fake.sentence() if status == "completed" else None,
            price=service.base_price + random.randint(-20, 50),
            address=customer.customer_profile[0].address if customer.customer_profile else None,  # FIXED
            notes=fake.sentence() if random.random() > 0.5 else None,
            rejection_reason="Customer cancelled" if status == "cancelled" else ("Professional unavailable" if status == "rejected" else None),
            created_at=requested_date,
            updated_at=datetime.utcnow()
        )


        db.session.add(service_request)


def init_db():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            name='Admin User',
            role='admin'
        )
        db.session.add(admin)

        print("Creating services...")
        services = [
            Service(name='House Cleaning', description='Complete house cleaning service', base_price=100, is_active=True),
            Service(name='Plumbing', description='Professional plumbing services', base_price=150, is_active=True),
            Service(name='Electrical', description='Electrical repair and installation', base_price=200, is_active=True),
            Service(name='Painting', description='Home and office painting service', base_price=180, is_active=True),
            Service(name='Carpentry', description='Furniture and woodwork services', base_price=170, is_active=True)
        ]
        
        for service in services:
            db.session.add(service)
        db.session.flush()

        print("Generating professionals...")
        professionals = generate_professionals()

        print("Generating customers...")
        customers = generate_customers()

        print("Generating service requests...")
        generate_service_requests(customers, professionals, services)

        try:
            db.session.commit()
            print("Database initialized successfully!")
        except Exception as e:
            print("Error initializing database:", str(e))
            db.session.rollback()

if __name__ == '__main__':
    init_db()
