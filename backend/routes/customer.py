from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import customer_required
from models.models import Customer, ServiceRequest

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@customer_required
def customer_dashboard():
    current_user_id = get_jwt_identity()
    customer = Customer.query.filter_by(user_id=current_user_id).first()
    
    # Get service requests made by this customer
    service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()
    
    active_requests = [req for req in service_requests if req.status in ['requested', 'assigned']]
    completed_requests = [req for req in service_requests if req.status == 'completed']
    
    return jsonify({
        'active_requests': len(active_requests),
        'completed_requests': len(completed_requests)
    }), 200

@customer_bp.route('/requests', methods=['GET'])
@jwt_required()
@customer_required
def get_requests():
    current_user_id = get_jwt_identity()
    customer = Customer.query.filter_by(user_id=current_user_id).first()
    requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()
    
    return jsonify([{
        'id': req.id,
        'status': req.status,
        'date_requested': req.date_requested
    } for req in requests]), 200
