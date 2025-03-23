from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from models.models import User

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

def professional_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'professional':
            return jsonify({'error': 'Professional access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

def customer_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'customer':
            return jsonify({'error': 'Customer access required'}), 403
        return fn(*args, **kwargs)
    return wrapper
