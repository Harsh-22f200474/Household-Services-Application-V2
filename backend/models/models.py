from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Required field
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'professional', 'customer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Add service_type_id for professionals
    service_type_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)


class Professional(db.Model):
    __tablename__ = 'professionals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer)  # years of experience
    description = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='professional_profile')


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    
    # Relationships
    user = db.relationship('User', backref='customer_profile')


class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, default=60)  # in minutes
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'base_price': self.base_price,
            'time_required': self.time_required,
            'is_active': self.is_active
        }


class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='requested')  # requested, assigned, completed, cancelled, rejected
    requested_date = db.Column(db.DateTime, nullable=False)
    scheduled_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    customer_rating = db.Column(db.Integer)
    customer_review = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Update relationships to use User model
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_requests')
    professional = db.relationship('User', foreign_keys=[professional_id], backref='professional_requests')
    service = db.relationship('Service', backref='service_requests')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'service_id': self.service_id,
            'service_name': self.service.name if self.service else None,
            'professional_id': self.professional_id,
            'professional_name': self.professional.name if self.professional else None,
            'status': self.status,
            'requested_date': self.requested_date.isoformat() if self.requested_date else None,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'customer_rating': self.customer_rating,
            'customer_review': self.customer_review,
            'price': self.price,
            'address': self.address,
            'notes': self.notes,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 