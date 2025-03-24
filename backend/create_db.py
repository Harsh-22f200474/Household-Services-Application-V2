from app import create_app
from extensions import db, bcrypt
from models.models import User, Professional, Customer, Service, ServiceRequest, Review

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(role='admin').first():
            # Properly hash the password using bcrypt
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=hashed_password,
                role='admin',
                is_active=True
            )
            
            try:
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully!")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin: {e}")

if __name__ == '__main__':
    init_db() 