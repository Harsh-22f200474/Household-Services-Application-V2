from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import professional_required
from models.models import Professional, ServiceRequest

professional_bp = Blueprint('professional', __name__)

@professional_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@professional_required
def professional_dashboard():
    current_user_id = get_jwt_identity()
    professional = Professional.query.filter_by(user_id=current_user_id).first()
    
    # Get service requests for this professional
    service_requests = ServiceRequest.query.filter_by(professional_id=professional.id).all()
    
    pending_requests = [req for req in service_requests if req.status == 'requested']
    active_requests = [req for req in service_requests if req.status == 'assigned']
    
    return jsonify({
        'is_verified': professional.is_verified,
        'pending_requests': len(pending_requests),
        'active_requests': len(active_requests),
        'service_type': professional.service_type
    }), 200

@professional_bp.route('/requests', methods=['GET'])
@jwt_required()
@professional_required
def get_requests():
    current_user_id = get_jwt_identity()
    professional = Professional.query.filter_by(user_id=current_user_id).first()
    requests = ServiceRequest.query.filter_by(professional_id=professional.id).all()
    
    return jsonify([{
        'id': req.id,
        'status': req.status,
        'date_requested': req.date_requested
    } for req in requests]), 200
