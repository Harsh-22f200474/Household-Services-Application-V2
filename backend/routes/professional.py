from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import professional_required
from models.models import Professional, ServiceRequest, User, Service
from extensions import db
from datetime import datetime

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

@professional_bp.route('/service-requests/available', methods=['GET'])
@jwt_required()
def get_available_requests():
    """Get all available service requests for the professional's service type"""
    try:
        current_user_id = get_jwt_identity()
        professional = User.query.get(current_user_id)
        
        if not professional or professional.role != 'professional':
            return jsonify({'error': 'Unauthorized access'}), 403
        
        available_requests = ServiceRequest.query.filter_by(
            status='requested',
            service_id=professional.service_type_id
        ).all()
        
        return jsonify([request.to_dict() for request in available_requests]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@professional_bp.route('/service-requests/my-requests', methods=['GET'])
@jwt_required()
def get_professional_requests():
    """Get all service requests assigned to the professional"""
    try:
        current_user_id = get_jwt_identity()
        requests = ServiceRequest.query.filter_by(professional_id=current_user_id).all()
        return jsonify([request.to_dict() for request in requests]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@professional_bp.route('/service-requests/<int:request_id>/accept', methods=['POST'])
@jwt_required()
def accept_request(request_id):
    """Accept a service request"""
    try:
        current_user_id = get_jwt_identity()
        service_request = ServiceRequest.query.get(request_id)
        
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404
            
        if service_request.status != 'requested':
            return jsonify({'error': 'Service request is not available'}), 400
            
        service_request.professional_id = current_user_id
        service_request.status = 'assigned'
        db.session.commit()
        
        return jsonify(service_request.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@professional_bp.route('/service-requests/<int:request_id>/complete', methods=['POST'])
@jwt_required()
def complete_request(request_id):
    """Mark a service request as completed"""
    try:
        current_user_id = get_jwt_identity()
        service_request = ServiceRequest.query.filter_by(
            id=request_id,
            professional_id=current_user_id
        ).first()
        
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404
            
        if service_request.status != 'assigned':
            return jsonify({'error': 'Can only complete assigned service requests'}), 400
            
        service_request.status = 'completed'
        service_request.completion_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify(service_request.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@professional_bp.route('/service-requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_request(request_id):
    """Reject a service request"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'reason' not in data:
            return jsonify({'error': 'Rejection reason is required'}), 400
            
        service_request = ServiceRequest.query.get(request_id)
        
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404
            
        if service_request.status != 'requested':
            return jsonify({'error': 'Can only reject pending service requests'}), 400
            
        service_request.status = 'rejected'
        service_request.rejection_reason = data['reason']
        db.session.commit()
        
        return jsonify(service_request.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
