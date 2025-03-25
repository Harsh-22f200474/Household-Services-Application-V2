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
    try:
        data = request.get_json()
        print("Registration data received:", data)
        
        # Check required fields
        required_fields = ['username', 'email', 'password', 'name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 400

        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            name=data['name'],
            role=data['role'],
            service_type_id=data.get('service_type_id') if data['role'] == 'professional' else None
        )

        db.session.add(new_user)
        db.session.flush()  # This gets us the user.id before committing

        # Create role-specific profile
        if data['role'] == 'professional':
            professional = Professional(
                user_id=new_user.id,
                service_type=str(data.get('service_type_id')),
                experience=data.get('experience', 0),
                description=data.get('description', ''),
                is_verified=False  # New professionals start unverified
            )
            db.session.add(professional)
        elif data['role'] == 'customer':
            customer = Customer(
                user_id=new_user.id,
                address=data.get('address', ''),
                phone=data.get('phone', '')
            )
            db.session.add(customer)

        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'name': new_user.name,
                'role': new_user.role
            }
        }), 201

    except Exception as e:
        print("Registration error:", str(e))
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check if professional is verified
        if user.role == 'professional':
            professional = Professional.query.filter_by(user_id=user.id).first()
            if not professional or not professional.is_verified:
                return jsonify({'error': 'Your account is pending admin approval'}), 403

        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
