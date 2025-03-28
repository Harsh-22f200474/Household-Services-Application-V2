from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt
from models import User

def role_required(role):
    """
    Decorator to check if the user has the required role
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt()['sub']
            user = User.query.get(user_id)
            if not user or user.role != role:
                return jsonify({
                    "category": "danger",
                    "message": f"{role} access required"
                }), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def admin_required():
    """
    Decorator to check if the user is an admin
    """
    return role_required('Admin')

def professional_required():
    """
    Decorator to check if the user is a professional
    """
    return role_required('Professional')

def customer_required():
    """
    Decorator to check if the user is a customer
    """
    return role_required('Customer') 