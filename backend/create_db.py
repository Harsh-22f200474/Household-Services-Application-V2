from app import create_app
from extensions import db, bcrypt
from models.models import User, Service, Professional

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.drop_all()
        db.create_all()
        
        print("Creating admin user...") # Debug print
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            name='Admin User',
            role='admin'
        )
        
        print("Creating services...") # Debug print
        # Create initial services
        services = [
            Service(
                name='House Cleaning',
                description='Complete house cleaning service',
                base_price=100,
                is_active=True
            ),
            Service(
                name='Plumbing',
                description='Professional plumbing services',
                base_price=150,
                is_active=True
            ),
            Service(
                name='Electrical',
                description='Electrical repair and installation',
                base_price=200,
                is_active=True
            )
        ]
        
        db.session.add(admin)
        for service in services:
            db.session.add(service)
        db.session.flush()

        print("Creating test professional...") # Debug print
        # Create a test professional
        professional = User(
            username='professional',
            email='professional@example.com',
            password_hash=bcrypt.generate_password_hash('professional123').decode('utf-8'),
            name='Test Professional',
            role='professional',
            service_type_id=1  # Assign to House Cleaning service
        )
        db.session.add(professional)
        db.session.flush()

        # Create professional profile
        prof_profile = Professional(
            user_id=professional.id,
            service_type='House Cleaning',
            experience=5,
            description='Experienced cleaner',
            is_verified=True
        )
        db.session.add(prof_profile)

        print("Creating test customer...") # Debug print
        # Create a test customer
        customer = User(
            username='customer',
            email='customer@example.com',
            password_hash=bcrypt.generate_password_hash('customer123').decode('utf-8'),
            name='Test Customer',
            role='customer'
        )
        db.session.add(customer)
        
        try:
            db.session.commit()
            print("Database initialized successfully!")
        except Exception as e:
            print("Error initializing database:", str(e))
            db.session.rollback()

if __name__ == '__main__':
    init_db() 