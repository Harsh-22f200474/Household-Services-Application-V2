from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin, Professional, Customer
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    approve = db.Column(db.Boolean, default=None)  # Will be set based on role in registration
    blocked = db.Column(db.Boolean, default=None)  # Will be set based on role in registration

    def __repr__(self):
        return f'<User {self.username}>'

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    service_type = db.Column(db.String(50))

    def __repr__(self):
        return f'<Service {self.name}>'
    
    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}


class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_of_accept_reject = db.Column(db.DateTime, nullable=True)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(20))  # requested, accepted, rejected , completed
    remarks = db.Column(db.String(200))

    def __repr__(self):
        return f'<ServiceRequest {self.id} - {self.service_status}>'

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating from 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    service_request = db.relationship('ServiceRequest', backref=db.backref('review', uselist=False))
    customer = db.relationship('User', foreign_keys=[customer_id], backref='reviews_given')
    professional = db.relationship('User', foreign_keys=[professional_id], backref='reviews_received')

    def __repr__(self):
        return f'<Review {self.id} - Rating: {self.rating}>'

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

class ProfessionalProfile(db.Model):
    __tablename__ = 'professional_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    full_name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(120), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    address = db.Column(db.String(200),nullable=False)
    pin_code = db.Column(db.String(6), nullable=False)
    reviews = db.Column(db.Float, default=0)  # Average rating calculated from Review model

    def __repr__(self):
        return f'<ProfessionalProfile {self.user_id} - {self.service_type}>'
    
    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

    def update_average_rating(self):
        """Update the average rating based on all reviews"""
        from sqlalchemy import func
        avg_rating = db.session.query(func.avg(Review.rating)).filter(
            Review.professional_id == self.user_id
        ).scalar()
        self.reviews = float(avg_rating) if avg_rating else 0.0
        db.session.commit()

class CustomerProfile(db.Model):
    __tablename__ = 'customer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    full_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200),nullable=False)
    pin_code = db.Column(db.String(6), nullable=False)

    def __repr__(self):
        return f'<CustomerProfile {self.full_name} - {self.pin_code}>'

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}
    
