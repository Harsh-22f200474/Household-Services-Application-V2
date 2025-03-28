from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models import db, CustomerProfile, ServiceRequest, Service, ProfessionalProfile, User, Review
from datetime import datetime

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customer/profile', methods=['POST'])
@jwt_required()
def create_customer_profile():
    """
    Create a customer profile
    ---
    tags:
      - Customer
    parameters:
      - name: profile
        in: body
        required: true
        schema:
          type: object
          properties:
            full_name:
              type: string
            address:
              type: string
            pin_code:
              type: string
    responses:
      200:
        description: Profile created successfully
      400:
        description: Invalid input data
    """
    data = request.get_json()
    user_id = get_jwt()['sub']
    
    if not all(k in data for k in ["full_name", "address", "pin_code"]):
        return jsonify({"category": "danger", "message": "Missing required fields"}), 400
    
    new_profile = CustomerProfile(
        user_id=user_id,
        full_name=data['full_name'],
        address=data['address'],
        pin_code=data['pin_code']
    )
    
    try:
        db.session.add(new_profile)
        db.session.commit()
        return jsonify({"category": "success", "message": "Profile created successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"category": "danger", "message": str(e)}), 500

@customer_bp.route('/customer/services', methods=['GET'])
@jwt_required()
def get_services():
    """
    Get all available services
    ---
    tags:
      - Customer
    responses:
      200:
        description: List of services
    """
    services = Service.query.all()
    return jsonify([service.as_dict() for service in services]), 200

@customer_bp.route('/customer/professionals/<service_type>', methods=['GET'])
@jwt_required()
def get_professionals_by_service(service_type):
    """
    Get professionals by service type
    ---
    tags:
      - Customer
    parameters:
      - name: service_type
        in: path
        type: string
        required: true
    responses:
      200:
        description: List of professionals
    """
    professionals = (
        ProfessionalProfile.query
        .join(User, ProfessionalProfile.user_id == User.id)
        .filter(
            ProfessionalProfile.service_type == service_type,
            User.approve == True,
            User.blocked == False
        )
        .all()
    )
    return jsonify([prof.as_dict() for prof in professionals]), 200

@customer_bp.route('/customer/request', methods=['POST'])
@jwt_required()
def create_service_request():
    """
    Create a service request
    ---
    tags:
      - Customer
    parameters:
      - name: request
        in: body
        required: true
        schema:
          type: object
          properties:
            service_id:
              type: integer
            professional_id:
              type: integer
            remarks:
              type: string
    responses:
      200:
        description: Request created successfully
      400:
        description: Invalid input data
    """
    data = request.get_json()
    user_id = get_jwt()['sub']
    
    if not all(k in data for k in ["service_id", "professional_id"]):
        return jsonify({"category": "danger", "message": "Missing required fields"}), 400
    
    new_request = ServiceRequest(
        service_id=data['service_id'],
        customer_id=user_id,
        professional_id=data['professional_id'],
        service_status='requested',
        remarks=data.get('remarks', '')
    )
    
    try:
        db.session.add(new_request)
        db.session.commit()
        return jsonify({"category": "success", "message": "Request created successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"category": "danger", "message": str(e)}), 500

@customer_bp.route('/customer/requests', methods=['GET'])
@jwt_required()
def get_customer_requests():
    """
    Get all service requests for a customer
    ---
    tags:
      - Customer
    responses:
      200:
        description: List of service requests
    """
    user_id = get_jwt()['sub']
    requests = ServiceRequest.query.filter_by(customer_id=user_id).all()
    return jsonify([request.as_dict() for request in requests]), 200 

@customer_bp.route('/services/search')
@jwt_required()
def search_services():
    location = request.args.get('location')
    pin_code = request.args.get('pin_code')
    service_type = request.args.get('service_type')
    
    # Start with base query
    query = Service.query
    
    if pin_code:
        # Join with ProfessionalProfile and filter by pin_code
        query = (
            Service.query
            .join(ProfessionalProfile, Service.service_type == ProfessionalProfile.service_type)
            .filter(ProfessionalProfile.pin_code == pin_code)
            .distinct()
        )
    
    if service_type:
        query = query.filter(Service.service_type == service_type)
    
    if location:
        # Join with ProfessionalProfile and filter by location
        query = (
            Service.query
            .join(ProfessionalProfile, Service.service_type == ProfessionalProfile.service_type)
            .filter(ProfessionalProfile.address.ilike(f'%{location}%'))
            .distinct()
        )
    
    try:
        services = query.all()
        return jsonify([service.as_dict() for service in services])
    except Exception as e:
        return jsonify({
            "category": "danger",
            "message": f"Error searching services: {str(e)}"
        }), 500

@customer_bp.route('/review/<int:service_request_id>', methods=['POST'])
@jwt_required()
def create_review(service_request_id):
    """Create a review for a completed service request"""
    current_user_id = get_jwt_identity()
    print(f"Debug - Attempting review creation: service_request_id={service_request_id}, current_user_id={current_user_id}")
    
    # Get the service request
    service_request = ServiceRequest.query.get_or_404(service_request_id)
    print(f"Debug - Service Request found: customer_id={service_request.customer_id}, status={service_request.service_status}")
    
    # Verify this is the customer's service request
    if service_request.customer_id != current_user_id:
        print(f"Debug - Authorization failed: request customer_id={service_request.customer_id} does not match current_user_id={current_user_id}")
        return jsonify({"error": "You are not authorized to review this service request", 
                       "message": "This service request belongs to a different customer"}), 403
    
    # Verify service is completed
    if service_request.service_status != 'completed':
        return jsonify({"error": "Can only review completed services",
                       "message": "Please wait until the service is marked as completed"}), 400
        
    # Check if review already exists
    existing_review = Review.query.filter_by(service_request_id=service_request_id).first()
    if existing_review:
        return jsonify({"error": "Review already exists",
                       "message": "You have already submitted a review for this service"}), 400
    
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    # Validate rating
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Invalid rating",
                       "message": "Rating must be between 1 and 5"}), 400
    
    try:
        # Create review
        review = Review(
            service_request_id=service_request_id,
            customer_id=current_user_id,
            professional_id=service_request.professional_id,
            rating=rating,
            comment=comment
        )
        
        db.session.add(review)
        
        # Update professional's average rating
        professional_profile = ProfessionalProfile.query.filter_by(
            user_id=service_request.professional_id
        ).first()
        if professional_profile:
            professional_profile.update_average_rating()
        
        db.session.commit()
        return jsonify({"message": "Review submitted successfully", "data": review.as_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error",
                       "message": f"Error saving review: {str(e)}"}), 500

@customer_bp.route('/reviews/given', methods=['GET'])
@jwt_required()
def get_my_reviews():
    """Get all reviews given by the current customer"""
    current_user_id = get_jwt_identity()
    reviews = Review.query.filter_by(customer_id=current_user_id).all()
    return jsonify([review.as_dict() for review in reviews])

@customer_bp.route('/professional/<int:professional_id>/reviews', methods=['GET'])
@jwt_required()
def get_professional_reviews(professional_id):
    """Get all reviews for a specific professional"""
    reviews = Review.query.filter_by(professional_id=professional_id).all()
    return jsonify([review.as_dict() for review in reviews])

@customer_bp.route('/customer/request/<int:request_id>/close', methods=['PUT'])
@jwt_required()
def close_service_request(request_id):
    """Close a service request by the customer"""
    current_user_id = get_jwt_identity()
    print(f"Debug - Attempting to close service request: request_id={request_id}, current_user_id={current_user_id}")
    print(f"Debug - Type of current_user_id: {type(current_user_id)}")
    
    # Get the service request
    service_request = ServiceRequest.query.get_or_404(request_id)
    print(f"Debug - Service Request found: customer_id={service_request.customer_id}, status={service_request.service_status}")
    print(f"Debug - Type of service_request.customer_id: {type(service_request.customer_id)}")
    
    # Convert IDs to integers for comparison
    current_user_id = int(current_user_id)
    customer_id = int(service_request.customer_id)
    
    print(f"Debug - After conversion - current_user_id: {current_user_id} ({type(current_user_id)}), customer_id: {customer_id} ({type(customer_id)})")
    
    # Verify this is the customer's service request
    if customer_id != current_user_id:
        print(f"Debug - Authorization failed: request customer_id={customer_id} does not match current_user_id={current_user_id}")
        return jsonify({
            "message": f"You are not authorized to close this service request. Request belongs to customer {customer_id}, but you are {current_user_id}",
            "category": "danger"
        }), 403
    
    # Verify service request is in accepted status
    if service_request.service_status != 'accepted':
        print(f"Debug - Invalid status: current status is {service_request.service_status}")
        return jsonify({
            "message": "Only accepted service requests can be closed",
            "category": "danger"
        }), 400
    
    try:
        # Update the service request status to completed
        service_request.service_status = 'completed'
        service_request.date_of_completion = datetime.utcnow()
        db.session.commit()
        print(f"Debug - Service request closed successfully")
        
        return jsonify({
            "message": "Service request closed successfully",
            "category": "success"
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Debug - Error closing service request: {str(e)}")
        return jsonify({
            "message": f"Error closing service request: {str(e)}",
            "category": "danger"
        }), 500