from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from models.models import User, Professional, Customer, Service, ServiceRequest
from extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        role=data['role']  # 'customer' or 'professional'
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Create profile based on role
        if data['role'] == 'customer':
            customer = Customer(
                user_id=new_user.id,
                address=data.get('address', ''),
                phone=data.get('phone', '')
            )
            db.session.add(customer)
        
        elif data['role'] == 'professional':
            professional = Professional(
                user_id=new_user.id,
                service_type=data.get('service_type', ''),
                experience=data.get('experience', 0),
                description=data.get('description', '')
            )
            db.session.add(professional)
        
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, data['password']):
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            # Determine dashboard URL and initial data based on role
            if user.role == 'admin':
                # Get initial admin dashboard data
                services_count = Service.query.count()
                pending_professionals = Professional.query.filter_by(is_verified=False).count()
                active_requests = ServiceRequest.query.filter_by(status='requested').count()
                
                response_data = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role
                    },
                    'dashboard_url': '/api/admin/dashboard',
                    'dashboard_data': {
                        'total_services': services_count,
                        'pending_verifications': pending_professionals,
                        'active_requests': active_requests
                    }
                }
            else:
                response_data = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role
                    },
                    'dashboard_url': f'/api/{user.role}/dashboard'
                }
            
            return jsonify(response_data), 200
        
        return jsonify({'error': 'Invalid email or password'}), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")  # For debugging
        return jsonify({'error': 'An error occurred during login'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a real application, you might want to blacklist the token
    return jsonify({"message": "Successfully logged out"}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'customer':
        profile = Customer.query.filter_by(user_id=user.id).first()
        profile_data = {
            'address': profile.address,
            'phone': profile.phone
        }
    elif user.role == 'professional':
        profile = Professional.query.filter_by(user_id=user.id).first()
        profile_data = {
            'service_type': profile.service_type,
            'experience': profile.experience,
            'description': profile.description,
            'is_verified': profile.is_verified
        }
    else:  # admin
        profile_data = {}

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'profile': profile_data
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    data = request.get_json()
    
    try:
        # Update basic user info
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
            
        # Update role-specific profile
        if user.role == 'customer':
            profile = Customer.query.filter_by(user_id=user.id).first()
            if 'address' in data:
                profile.address = data['address']
            if 'phone' in data:
                profile.phone = data['phone']
                
        elif user.role == 'professional':
            profile = Professional.query.filter_by(user_id=user.id).first()
            if 'service_type' in data:
                profile.service_type = data['service_type']
            if 'experience' in data:
                profile.experience = data['experience']
            if 'description' in data:
                profile.description = data['description']
                
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
