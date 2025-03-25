from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import customer_required
from models.models import Customer, ServiceRequest, Service, User, Professional
from extensions import db
from datetime import datetime
from flask_cors import CORS
customer_bp = Blueprint('customer', __name__)
CORS(customer_bp, resources={r"/api/customer/*": {"origins": ["http://localhost:8080"]}})

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

@customer_bp.route('/services', methods=['GET'])
@jwt_required()
def get_available_services():
    """Get all available services for customers"""
    try:
        services = Service.query.filter_by(is_active=True).all()
        return jsonify([service.to_dict() for service in services]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/service-requests', methods=['POST'])
@jwt_required()
def create_service_request():
    """Create a new service request"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service_id', 'requested_date', 'address']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get service price
        service = Service.query.get(data['service_id'])
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        new_request = ServiceRequest(
            customer_id=current_user_id,
            service_id=data['service_id'],
            requested_date=datetime.fromisoformat(data['requested_date']),
            price=service.base_price,
            address=data['address'],
            notes=data.get('notes', ''),
            status='requested'
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        return jsonify(new_request.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/service-requests', methods=['GET'])
@jwt_required()
def get_customer_requests():
    """Get all service requests for the current customer"""
    try:
        current_user_id = get_jwt_identity()
        requests = ServiceRequest.query.filter_by(customer_id=current_user_id).all()
        return jsonify([request.to_dict() for request in requests]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/service-requests/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_service_request(request_id):
    """Cancel a service request"""
    try:
        current_user_id = get_jwt_identity()
        service_request = ServiceRequest.query.filter_by(
            id=request_id,
            customer_id=current_user_id
        ).first()
        
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404
            
        if service_request.status not in ['requested', 'assigned']:
            return jsonify({'error': 'Cannot cancel completed or cancelled service requests'}), 400
            
        service_request.status = 'cancelled'
        db.session.commit()
        
        return jsonify(service_request.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/service-requests/<int:request_id>/review', methods=['POST'])
@jwt_required()
def add_review(request_id):
    """Add a review for a completed service request"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'rating' not in data or 'review' not in data:
            return jsonify({'error': 'Rating and review are required'}), 400
            
        service_request = ServiceRequest.query.filter_by(
            id=request_id,
            customer_id=current_user_id
        ).first()
        
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404
            
        if service_request.status != 'completed':
            return jsonify({'error': 'Can only review completed service requests'}), 400
            
        service_request.customer_rating = data['rating']
        service_request.customer_review = data['review']
        db.session.commit()
        
        return jsonify(service_request.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/service-requests/<int:request_id>', methods=['PUT'])
@jwt_required()
def update_service_request(request_id):
    """Update a service request"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        service_request = ServiceRequest.query.filter_by(
            id=request_id,
            customer_id=current_user_id
        ).first()
        
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404
            
        if service_request.status != 'requested':
            return jsonify({'error': 'Can only edit pending service requests'}), 400
        
        # Update allowed fields
        if 'requested_date' in data:
            service_request.requested_date = datetime.fromisoformat(data['requested_date'])
        if 'address' in data:
            service_request.address = data['address']
        if 'notes' in data:
            service_request.notes = data['notes']
            
        db.session.commit()
        
        return jsonify(service_request.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/services/<int:service_id>/professionals', methods=['GET'])
@jwt_required()
def get_service_professionals(service_id):
    try:
        professionals = User.query.join(Professional).filter(
            User.role == 'professional',
            User.service_type_id == service_id,
            Professional.is_verified == True
        ).all()
        
        return jsonify([{
            'id': prof.id,
            'name': prof.name,
            'rating': calculate_professional_rating(prof.id),
            'reviews_count': get_professional_reviews_count(prof.id),
            'experience': prof.professional_profile[0].experience,
            'completed_services': get_completed_services_count(prof.id)
        } for prof in professionals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_professional_rating(professional_id):
    completed_requests = ServiceRequest.query.filter_by(
        professional_id=professional_id,
        status='completed'
    ).all()
    
    if not completed_requests:
        return 0
        
    total_rating = sum(req.customer_rating or 0 for req in completed_requests)
    return round(total_rating / len(completed_requests), 1)

def get_professional_reviews_count(professional_id):
    return ServiceRequest.query.filter_by(
        professional_id=professional_id,
        status='completed'
    ).filter(ServiceRequest.customer_rating.isnot(None)).count()

def get_completed_services_count(professional_id):
    return ServiceRequest.query.filter_by(
        professional_id=professional_id,
        status='completed'
    ).count()

@customer_bp.route('/statistics/requests', methods=['GET'])
@jwt_required()
@customer_required
def get_customer_statistics():
    """Retrieve statistics related to customer's service requests"""
    try:
        current_user_id = get_jwt_identity()
        customer = Customer.query.filter_by(user_id=current_user_id).first()

        if not customer:
            return jsonify({'error': 'Customer not found'}), 404

        total_requests = ServiceRequest.query.filter_by(customer_id=customer.id).count()
        completed_requests = ServiceRequest.query.filter_by(customer_id=customer.id, status='completed').count()
        pending_requests = ServiceRequest.query.filter(ServiceRequest.customer_id == customer.id, ServiceRequest.status.in_(['requested', 'assigned'])).count()

        return jsonify({
            'total_requests': total_requests,
            'completed_requests': completed_requests,
            'pending_requests': pending_requests
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500