from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from models import db, ProfessionalProfile, ServiceRequest, User, Review, CustomerProfile, Service
from datetime import datetime, timedelta
from routes.file import allowed_file
from utils.helpers import save_file

professional_bp = Blueprint('professional', __name__)

@professional_bp.route('/professional/profile', methods=['POST'])
@jwt_required()
def create_professional_profile():
    """
    Create or update a professional profile
    ---
    tags:
      - Professional
    parameters:
      - name: profile
        in: body
        required: true
        schema:
          type: object
          properties:
            full_name:
              type: string
            service_type:
              type: string
            experience:
              type: string
            address:
              type: string
            pin_code:
              type: string
    responses:
      200:
        description: Profile created/updated successfully
      400:
        description: Invalid input data
    """
    data = request.form.to_dict()
    user_id = get_jwt()['sub']
    
    if not all(k in data for k in ["full_name", "service_type", "experience", "address", "pin_code"]):
        return jsonify({"category": "danger", "message": "Missing required fields"}), 400
    
    # Check if profile already exists
    existing_profile = ProfessionalProfile.query.filter_by(user_id=user_id).first()
    
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            if not allowed_file(file.filename):
                return jsonify({"category": "danger", "message": "Invalid file type"}), 400
            
            filename = secure_filename(file.filename)
            saved_filename = save_file(file)
            
            if not saved_filename:
                return jsonify({"category": "danger", "message": "Error saving file"}), 500
        else:
            saved_filename = existing_profile.filename if existing_profile else None
    else:
        saved_filename = existing_profile.filename if existing_profile else None
    
    try:
        if existing_profile:
            # Update existing profile
            existing_profile.full_name = data['full_name']
            existing_profile.service_type = data['service_type']
            existing_profile.experience = data['experience']
            existing_profile.address = data['address']
            existing_profile.pin_code = data['pin_code']
            if saved_filename:
                existing_profile.filename = saved_filename
        else:
            # Create new profile
            new_profile = ProfessionalProfile(
                user_id=user_id,
                full_name=data['full_name'],
                service_type=data['service_type'],
                experience=data['experience'],
                address=data['address'],
                pin_code=data['pin_code'],
                filename=saved_filename
            )
            db.session.add(new_profile)
        
        db.session.commit()
        return jsonify({"category": "success", "message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"category": "danger", "message": str(e)}), 500

@professional_bp.route('/professional/requests', methods=['GET'])
@jwt_required()
def get_professional_requests():
    """
    Get all service requests for a professional
    ---
    tags:
      - Professional
    responses:
      200:
        description: List of service requests
    """
    user_id = get_jwt()['sub']
    
    # Get all service requests for this professional
    requests = ServiceRequest.query.filter_by(professional_id=user_id).all()
    
    # Get all customer IDs and service IDs from these requests
    customer_ids = set(req.customer_id for req in requests)
    service_ids = set(req.service_id for req in requests)
    
    # Get customer profiles and services
    customers = CustomerProfile.query.filter(CustomerProfile.user_id.in_(customer_ids)).all()
    services = Service.query.filter(Service.id.in_(service_ids)).all()
    
    # Create dictionaries for easy lookup
    customer_dict = {cust.user_id: cust.as_dict() for cust in customers}
    service_dict = {service.id: service.as_dict() for service in services}
    
    return jsonify({
        "requests": [request.as_dict() for request in requests],
        "customers": customer_dict,
        "services": service_dict
    }), 200

@professional_bp.route('/professional/request/<int:request_id>', methods=['PUT'])
@jwt_required()
def update_request_status(request_id):
    """
    Update service request status
    ---
    tags:
      - Professional
    parameters:
      - name: request_id
        in: path
        type: integer
        required: true
      - name: status
        in: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [accepted, rejected, completed]
    responses:
      200:
        description: Status updated successfully
      404:
        description: Request not found
    """
    user_id = get_jwt()['sub']
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({"category": "danger", "message": "Status is required"}), 400
        
    service_request = ServiceRequest.query.filter_by(id=request_id, professional_id=user_id).first()
    if not service_request:
        return jsonify({"category": "danger", "message": "Request not found"}), 404
        
    service_request.service_status = data['status']
    service_request.date_of_accept_reject = datetime.utcnow()
    
    if data['status'] == 'completed':
        service_request.date_of_completion = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({"category": "success", "message": "Status updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"category": "danger", "message": str(e)}), 500

@professional_bp.route('/reviews/received', methods=['GET'])
@jwt_required()
def get_my_reviews():
    """Get all reviews received by the current professional"""
    current_user_id = get_jwt_identity()
    
    # Optional query parameters for filtering
    rating = request.args.get('rating', type=int)  # Filter by specific rating
    sort_by = request.args.get('sort_by', 'created_at')  # Sort by date or rating
    order = request.args.get('order', 'desc')  # asc or desc
    
    # Base query
    query = Review.query.filter_by(professional_id=current_user_id)
    
    # Apply rating filter if specified
    if rating:
        query = query.filter_by(rating=rating)
    
    # Apply sorting
    if sort_by == 'rating':
        query = query.order_by(Review.rating.desc() if order == 'desc' else Review.rating.asc())
    else:  # default sort by date
        query = query.order_by(Review.created_at.desc() if order == 'desc' else Review.created_at.asc())
    
    reviews = query.all()
    
    # Get customer details
    customer_ids = set(review.customer_id for review in reviews)
    customers = CustomerProfile.query.filter(CustomerProfile.user_id.in_(customer_ids)).all()
    customer_dict = {cust.user_id: cust.as_dict() for cust in customers}
    
    return jsonify({
        "reviews": [review.as_dict() for review in reviews],
        "customers": customer_dict
    })

@professional_bp.route('/reviews/stats', methods=['GET'])
@jwt_required()
def get_review_stats():
    """Get statistics about the professional's reviews"""
    current_user_id = get_jwt_identity()
    
    from sqlalchemy import func
    
    # Get total number of reviews and average rating
    stats = db.session.query(
        func.count(Review.id).label('total_reviews'),
        func.avg(Review.rating).label('average_rating')
    ).filter_by(professional_id=current_user_id).first()
    
    # Get rating distribution
    rating_dist = db.session.query(
        Review.rating,
        func.count(Review.id).label('count')
    ).filter_by(professional_id=current_user_id).group_by(Review.rating).all()
    
    # Format rating distribution
    distribution = {rating: count for rating, count in rating_dist}
    
    return jsonify({
        'total_reviews': stats[0],
        'average_rating': float(stats[1]) if stats[1] else 0.0,
        'rating_distribution': {
            '5_star': distribution.get(5, 0),
            '4_star': distribution.get(4, 0),
            '3_star': distribution.get(3, 0),
            '2_star': distribution.get(2, 0),
            '1_star': distribution.get(1, 0)
        }
    })

@professional_bp.route('/professional/profile', methods=['GET'])
@jwt_required()
def get_professional_profile():
    """
    Get professional profile
    ---
    tags:
      - Professional
    responses:
      200:
        description: Profile data retrieved successfully
      404:
        description: Profile not found
    """
    user_id = get_jwt()['sub']
    
    # Get user data for username
    user = User.query.get(user_id)
    if not user:
        return jsonify({"category": "danger", "message": "User not found"}), 404
        
    # Get professional profile
    profile = ProfessionalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({
            "username": user.username,
            "full_name": "",
            "service_type": "",
            "experience": "",
            "address": "",
            "pin_code": ""
        }), 200
        
    return jsonify({
        "username": user.username,
        "full_name": profile.full_name,
        "service_type": profile.service_type,
        "experience": profile.experience,
        "address": profile.address,
        "pin_code": profile.pin_code
    }), 200

@professional_bp.route('/professional/search', methods=['POST'])
@jwt_required()
def search_service_requests():
    """Search service requests for a professional"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'search_type' not in data or 'search_text' not in data:
        return jsonify({
            "category": "danger",
            "message": "Missing search parameters"
        }), 400
    
    # Base query for service requests
    query = ServiceRequest.query.filter_by(professional_id=current_user_id)
    
    # Get all service IDs and customer IDs for later use
    service_ids = set()
    customer_ids = set()
    
    if data['search_type'] == 'date':
        try:
            search_date = datetime.strptime(data['search_text'], '%Y-%m-%d').date()
            query = query.filter(
                db.func.date(ServiceRequest.date_of_request) == search_date
            )
        except ValueError:
            return jsonify({
                "category": "danger",
                "message": "Invalid date format. Please use YYYY-MM-DD"
            }), 400
    elif data['search_type'] == 'location':
        # Join with CustomerProfile to search by location
        query = query.join(
            CustomerProfile,
            ServiceRequest.customer_id == CustomerProfile.user_id
        ).filter(CustomerProfile.address.ilike(f"%{data['search_text']}%"))
    elif data['search_type'] == 'pin':
        # Join with CustomerProfile to search by PIN
        query = query.join(
            CustomerProfile,
            ServiceRequest.customer_id == CustomerProfile.user_id
        ).filter(CustomerProfile.pin_code == data['search_text'])
    
    # Execute query
    requests = query.all()
    
    # Collect service and customer IDs
    for req in requests:
        service_ids.add(req.service_id)
        customer_ids.add(req.customer_id)
    
    # Get related data
    services = Service.query.filter(Service.id.in_(service_ids)).all()
    customers = CustomerProfile.query.filter(CustomerProfile.user_id.in_(customer_ids)).all()
    
    # Create lookup dictionaries
    service_dict = {s.id: s.as_dict() for s in services}
    customer_dict = {c.user_id: c.as_dict() for c in customers}
    
    # Format response data
    formatted_requests = []
    for req in requests:
        formatted_requests.append({
            **req.as_dict(),
            'customer_name': customer_dict.get(req.customer_id, {}).get('full_name', 'Unknown'),
            'service_name': service_dict.get(req.service_id, {}).get('name', 'Unknown')
        })
    
    return jsonify({
        "category": "success",
        "message": f"Found {len(formatted_requests)} requests",
        "data": {
            "service_requests": formatted_requests
        }
    })

@professional_bp.route('/professional/summary/reviews/<int:user_id>', methods=['GET'])
@jwt_required()
def get_reviews_summary(user_id):
    """Get summary of reviews for a professional"""
    # Verify the requesting user is the same as the profile being accessed
    current_user_id = get_jwt_identity()
    if int(current_user_id) != int(user_id):
        return jsonify({
            "category": "danger",
            "message": "Unauthorized access"
        }), 403
    
    # Get reviews with customer names
    reviews = db.session.query(
        Review,
        CustomerProfile.full_name
    ).join(
        CustomerProfile,
        Review.customer_id == CustomerProfile.user_id
    ).filter(
        Review.professional_id == user_id
    ).all()
    
    # Format the data
    formatted_reviews = [{
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at,
        'full_name': full_name
    } for review, full_name in reviews]
    
    return jsonify(formatted_reviews)

@professional_bp.route('/professional/summary/service_requests/<int:user_id>', methods=['GET'])
@jwt_required()
def get_service_requests_summary(user_id):
    """Get summary of service requests for a professional"""
    # Verify the requesting user is the same as the profile being accessed
    current_user_id = get_jwt_identity()
    if int(current_user_id) != int(user_id):
        return jsonify({
            "category": "danger",
            "message": "Unauthorized access"
        }), 403
    
    # Get all service requests for this professional
    service_requests = ServiceRequest.query.filter_by(professional_id=user_id).all()
    
    # Return the complete service request objects so frontend can categorize them
    return jsonify([
        {
            'id': req.id,
            'customer_id': req.customer_id,
            'professional_id': req.professional_id,
            'service_id': req.service_id,
            'service_status': req.service_status,
            'date_of_request': req.date_of_request.isoformat() if req.date_of_request else None,
            'date_of_accept_reject': req.date_of_accept_reject.isoformat() if req.date_of_accept_reject else None,
            'date_of_completion': req.date_of_completion.isoformat() if req.date_of_completion else None
        } for req in service_requests
    ])