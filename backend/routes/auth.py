from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, CustomerProfile, ProfessionalProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - name: user
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
            role:
              type: string
              enum: [Admin, Professional, Customer]
    responses:
      200:
        description: User registered successfully
      400:
        description: Invalid input or user already exists
    """
    data = request.get_json()
    
    if not all(k in data for k in ["username", "password", "role"]):
        return jsonify({"category": "danger", "message": "Missing required fields"}), 400
        
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"category": "danger", "message": "Username already exists"}), 400
        
    hashed_password = generate_password_hash(data['password'])
    
    # Set defaults based on role
    approve = True
    blocked = False
    
    # Professionals need admin approval
    if data['role'] == 'Professional':
        approve = False
        blocked = True
    
    new_user = User(
        username=data['username'],
        password=hashed_password,
        role=data['role'],
        approve=approve,
        blocked=blocked
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        message = "User registered successfully"
        if data['role'] == 'Professional':
            message = "Professional registered successfully. Please wait for admin approval."
            
        return jsonify({"category": "success", "message": message}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"category": "danger", "message": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    ---
    tags:
      - Authentication
    parameters:
      - name: credentials
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    
    if not all(k in data for k in ["username", "password"]):
        return jsonify({"category": "danger", "message": "Missing required fields"}), 400
        
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"category": "danger", "message": "Invalid username or password"}), 401
        
    if user.blocked:
        return jsonify({"category": "danger", "message": "Your account is blocked"}), 401
        
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "category": "success",
        "message": "Login successful",
        "access_token": access_token,
        "role": user.role,
        "approve": user.approve
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Logout successful
    """
    return jsonify({"category": "success", "message": "Logout successful"}), 200

@auth_bp.route('/get-claims', methods=['GET'])
@jwt_required()
def get_claims():
    """
    Get user claims from JWT token
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: User claims retrieved successfully
      401:
        description: Invalid or missing token
    """
    try:
        claims = get_jwt()
        user = User.query.get(claims['sub'])
        
        if not user:
            return jsonify({
                "category": "danger",
                "message": "User not found"
            }), 404
            
        redirect = None
        if user.role in ['Customer', 'Professional']:
            # For customers and professionals, check if profile is complete
            profile = None
            if user.role == 'Customer':
                profile = CustomerProfile.query.filter_by(user_id=user.id).first()
            else:
                profile = ProfessionalProfile.query.filter_by(user_id=user.id).first()
                
            if not profile:
                redirect = f"{user.role.lower()}_profile"
            else:
                redirect = f"{user.role.lower()}_dashboard"
        
        return jsonify({
            "category": "success",
            "message": "Claims retrieved successfully",
            "claims": {
                "user_id": user.id,
                "role": user.role,
                "redirect": redirect,
                "approved": user.approve,
                "blocked": user.blocked
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "category": "danger",
            "message": f"Error retrieving claims: {str(e)}"
        }), 500

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """
    Login admin user
    ---
    tags:
      - Authentication
    parameters:
      - name: credentials
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    
    if not all(k in data for k in ["username", "password"]):
        return jsonify({"category": "danger", "message": "Missing required fields"}), 400
        
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"category": "danger", "message": "Invalid username or password"}), 401
        
    if user.role != 'Admin':
        return jsonify({"category": "danger", "message": "Access denied. Admin privileges required."}), 403
        
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "category": "success",
        "message": "Login successful",
        "access_token": access_token,
        "role": user.role
    }), 200 