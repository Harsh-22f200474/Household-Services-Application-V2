from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import User, Professional, Customer, Service, ServiceRequest, Review
from extensions import db
from utils.decorators import admin_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Services Management
@admin_bp.route('/services', methods=['GET'])
@jwt_required()
@admin_required
def get_services():
    try:
        services = Service.query.all()
        return jsonify([{
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': service.base_price,
            'time_required': service.time_required,
            'is_active': service.is_active
        } for service in services]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services', methods=['POST'])
@jwt_required()
@admin_required
def create_service():
    try:
        # Print request data for debugging
        print("Request Headers:", request.headers)
        print("Request Data:", request.get_json())
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['name', 'description', 'base_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        new_service = Service(
            name=data['name'],
            description=data['description'],
            base_price=float(data['base_price']),
            time_required=data.get('time_required', 60)
        )
        
        db.session.add(new_service)
        db.session.commit()
        
        return jsonify({
            'message': 'Service created successfully',
            'service': {
                'id': new_service.id,
                'name': new_service.name,
                'description': new_service.description,
                'base_price': new_service.base_price
            }
        }), 201
        
    except Exception as e:
        print(f"Error creating service: {str(e)}")  # Debug print
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/services/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_service(id):
    service = Service.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'name' in data:
            service.name = data['name']
        if 'description' in data:
            service.description = data['description']
        if 'base_price' in data:
            service.base_price = data['base_price']
        if 'time_required' in data:
            service.time_required = data['time_required']
        
        db.session.commit()
        return jsonify({'message': 'Service updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/services/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_service(id):
    service = Service.query.get_or_404(id)
    
    try:
        db.session.delete(service)
        db.session.commit()
        return jsonify({'message': 'Service deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Professional Management
@admin_bp.route('/professionals', methods=['GET'])
@jwt_required()
@admin_required
def get_professionals():
    professionals = Professional.query.all()
    return jsonify([{
        'id': prof.id,
        'user_id': prof.user_id,
        'name': prof.user.username,
        'service_type': prof.service_type,
        'experience': prof.experience,
        'is_verified': prof.is_verified
    } for prof in professionals]), 200

@admin_bp.route('/professionals/<int:id>/verify', methods=['POST'])
@jwt_required()
@admin_required
def verify_professional(id):
    professional = Professional.query.get_or_404(id)
    
    try:
        professional.is_verified = True
        db.session.commit()
        return jsonify({'message': 'Professional verified successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/professionals/<int:id>/block', methods=['POST'])
@jwt_required()
@admin_required
def block_professional(id):
    professional = Professional.query.get_or_404(id)
    
    try:
        # Block both professional and associated user
        professional.is_verified = False
        professional.user.is_active = False
        db.session.commit()
        return jsonify({'message': 'Professional blocked successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Service Requests Management
@admin_bp.route('/service-requests', methods=['GET'])
@jwt_required()
@admin_required
def get_service_requests():
    requests = ServiceRequest.query.all()
    return jsonify([{
        'id': req.id,
        'service_id': req.service_id,
        'customer_name': req.customer.user.username,
        'professional_name': req.professional.user.username if req.professional else None,
        'status': req.status,
        'date_requested': req.date_requested.strftime('%Y-%m-%d %H:%M:%S'),
        'date_completed': req.date_completed.strftime('%Y-%m-%d %H:%M:%S') if req.date_completed else None
    } for req in requests]), 200

# Statistics and Summary
@admin_bp.route('/statistics/ratings', methods=['GET'])
@jwt_required()
@admin_required
def get_rating_statistics():
    # Get rating distribution (1-5 stars)
    ratings = db.session.query(
        Review.rating,
        db.func.count(Review.id)
    ).group_by(Review.rating).all()
    
    # Convert to format needed for chart
    rating_data = [0] * 5  # Initialize array for 1-5 stars
    for rating, count in ratings:
        rating_data[rating-1] = count
    
    return jsonify(rating_data), 200

@admin_bp.route('/statistics/requests', methods=['GET'])
@jwt_required()
@admin_required
def get_request_statistics():
    # Get request counts by status
    status_counts = db.session.query(
        ServiceRequest.status,
        db.func.count(ServiceRequest.id)
    ).group_by(ServiceRequest.status).all()
    
    # Convert to format needed for chart
    status_data = {
        'requested': 0,
        'assigned': 0,
        'completed': 0,
        'cancelled': 0
    }
    for status, count in status_counts:
        status_data[status] = count
    
    return jsonify(list(status_data.values())), 200

# Search Functionality
@admin_bp.route('/search', methods=['GET'])
@jwt_required()
@admin_required
def search():
    search_type = request.args.get('type', 'services')
    query = request.args.get('query', '')
    
    if search_type == 'services':
        results = Service.query.filter(Service.name.ilike(f'%{query}%')).all()
        return jsonify([{
            'id': service.id,
            'name': service.name,
            'details': f'${service.base_price}'
        } for service in results]), 200
        
    elif search_type == 'professionals':
        results = Professional.query.join(User).filter(
            User.username.ilike(f'%{query}%')
        ).all()
        return jsonify([{
            'id': prof.id,
            'name': prof.user.username,
            'details': f'{prof.service_type} - {prof.experience} years'
        } for prof in results]), 200
        
    elif search_type == 'customers':
        results = Customer.query.join(User).filter(
            User.username.ilike(f'%{query}%')
        ).all()
        return jsonify([{
            'id': cust.id,
            'name': cust.user.username,
            'details': cust.address
        } for cust in results]), 200
    
    return jsonify({'error': 'Invalid search type'}), 400
