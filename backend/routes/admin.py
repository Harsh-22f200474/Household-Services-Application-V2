from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt
from models import db, Service, User, ProfessionalProfile, ServiceRequest, CustomerProfile, Review
from functools import wraps
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from sqlalchemy import or_, func

admin_bp = Blueprint('admin', __name__)

# Add configuration for reports directory
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt()['sub']
            user = User.query.get(user_id)
            if not user or user.role != 'Admin':
                return jsonify({"category": "danger", "message": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@admin_bp.route('/admin/service', methods=['POST'])
@jwt_required()
@admin_required()
def create_service():
    """
    Create a new service
    ---
    tags:
      - Admin
    parameters:
      - name: service
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            price:
              type: number
            description:
              type: string
            service_type:
              type: string
    responses:
      200:
        description: Service created successfully
      400:
        description: Invalid input data
    """
    data = request.get_json()
    
    if not all(k in data for k in ["name", "price", "description", "service_type"]):
        return jsonify({"category": "danger", "message": "Missing required fields"}), 400
    
    new_service = Service(
        name=data['name'],
        price=data['price'],
        description=data['description'],
        service_type=data['service_type']
    )
    
    try:
        db.session.add(new_service)
        db.session.commit()
        return jsonify({"category": "success", "message": "Service created successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"category": "danger", "message": str(e)}), 500

@admin_bp.route('/admin/service/<int:service_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_service(service_id):
    """
    Update an existing service
    ---
    tags:
      - Admin
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
      - name: service
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            price:
              type: number
            description:
              type: string
            service_type:
              type: string
    responses:
      200:
        description: Service updated successfully
      404:
        description: Service not found
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"category": "danger", "message": "No data provided"}), 400

        service = Service.query.get(service_id)
        if not service:
            return jsonify({"category": "danger", "message": "Service not found"}), 404
        
        # Validate required fields
        required_fields = ["name", "price", "description", "service_type"]
        if not all(key in data for key in required_fields):
            return jsonify({
                "category": "danger", 
                "message": f"Missing required fields. Required: {', '.join(required_fields)}"
            }), 400

        # Validate price is a number
        try:
            price = float(data['price'])
            if price < 0:
                return jsonify({"category": "danger", "message": "Price cannot be negative"}), 400
            data['price'] = price
        except (ValueError, TypeError):
            return jsonify({"category": "danger", "message": "Invalid price format"}), 400

        # Update service attributes
        service.name = data['name']
        service.price = data['price']
        service.description = data['description']
        service.service_type = data['service_type']
    
        db.session.commit()
        return jsonify({
            "category": "success", 
            "message": "Service updated successfully",
            "service": service.as_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating service {service_id}: {str(e)}")  # Log the error
        return jsonify({"category": "danger", "message": f"Error updating service: {str(e)}"}), 500

@admin_bp.route('/admin/service/<int:service_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_service(service_id):
    """
    Delete a service
    ---
    tags:
      - Admin
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Service deleted successfully
      404:
        description: Service not found
    """
    try:
        service = Service.query.get(service_id)
        if not service:
            return jsonify({"category": "danger", "message": "Service not found"}), 404

        # Check if service is being used in any service requests
        service_requests = ServiceRequest.query.filter_by(service_id=service_id).first()
        if service_requests:
            return jsonify({
                "category": "danger", 
                "message": "Cannot delete service as it has associated service requests"
            }), 400

        db.session.delete(service)
        db.session.commit()
        
        return jsonify({
            "category": "success",
            "message": "Service deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting service {service_id}: {str(e)}")  # Log the error
        return jsonify({"category": "danger", "message": f"Error deleting service: {str(e)}"}), 500

@admin_bp.route('/admin/professionals', methods=['GET'])
@jwt_required()
@admin_required()
def get_professionals():
    """
    Get all professionals
    ---
    tags:
      - Admin
    responses:
      200:
        description: List of professionals
    """
    professionals = (
        ProfessionalProfile.query
        .join(User, ProfessionalProfile.user_id == User.id)
        .add_columns(User.approve, User.blocked)
        .all()
    )
    return jsonify([{**prof[0].as_dict(), 'approve': prof[1], 'blocked': prof[2]} for prof in professionals]), 200

@admin_bp.route('/admin/professional/<int:user_id>/approve', methods=['PUT'])
@jwt_required()
@admin_required()
def approve_professional(user_id):
    """
    Approve or disapprove a professional
    ---
    tags:
      - Admin
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: status
        in: body
        required: true
        schema:
          type: object
          properties:
            approve:
              type: boolean
    responses:
      200:
        description: Professional status updated successfully
      404:
        description: Professional not found
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"category": "danger", "message": "No data provided"}), 400
            
        if 'approve' not in data:
            return jsonify({"category": "danger", "message": "Approval status is required"}), 400
        
        if not isinstance(data['approve'], bool):
            return jsonify({"category": "danger", "message": "Approval status must be a boolean"}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"category": "danger", "message": "User not found"}), 404
            
        if user.role != 'Professional':
            return jsonify({"category": "danger", "message": "User is not a professional"}), 400
        
        # Get professional profile to verify it exists
        prof_profile = ProfessionalProfile.query.filter_by(user_id=user_id).first()
        if not prof_profile:
            return jsonify({"category": "danger", "message": "Professional profile not found"}), 404
        
        user.approve = data['approve']
        db.session.commit()
        
        return jsonify({
            "category": "success", 
            "message": f"Professional {prof_profile.full_name} has been {'approved' if data['approve'] else 'rejected'}",
            "approve": user.approve
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error approving professional {user_id}: {str(e)}")  # Log the error
        return jsonify({"category": "danger", "message": f"Database error: {str(e)}"}), 500

@admin_bp.route('/admin/professional/<int:user_id>/block', methods=['PUT'])
@jwt_required()
@admin_required()
def block_professional(user_id):
    """
    Block or unblock a professional
    ---
    tags:
      - Admin
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: status
        in: body
        required: true
        schema:
          type: object
          properties:
            blocked:
              type: boolean
    responses:
      200:
        description: Professional block status updated successfully
      404:
        description: Professional not found
    """
    data = request.get_json()
    
    if 'blocked' not in data:
        return jsonify({"category": "danger", "message": "Block status is required"}), 400
    
    user = User.query.get(user_id)
    if not user or user.role != 'Professional':
        return jsonify({"category": "danger", "message": "Professional not found"}), 404
    
    user.blocked = data['blocked']
    
    try:
        db.session.commit()
        return jsonify({"category": "success", "message": "Professional block status updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"category": "danger", "message": str(e)}), 500

@admin_bp.route('/admin/services', methods=['GET'])
@jwt_required()
@admin_required()
def get_services():
    """
    Get all services
    ---
    tags:
      - Admin
    responses:
      200:
        description: List of all services
    """
    try:
        services = Service.query.all()
        return jsonify([service.as_dict() for service in services]), 200
    except Exception as e:
        return jsonify({"category": "danger", "message": str(e)}), 500

@admin_bp.route('/admin/service-requests', methods=['GET'])
@jwt_required()
@admin_required()
def get_service_requests():
    """
    Get all service requests with professional details
    ---
    tags:
      - Admin
    responses:
      200:
        description: List of all service requests and professional details
    """
    try:
        # Get all service requests
        requests = ServiceRequest.query.all()
        
        # Get all professionals involved in these requests
        professional_ids = set(req.professional_id for req in requests)
        professionals = ProfessionalProfile.query.filter(
            ProfessionalProfile.user_id.in_(professional_ids)
        ).all()
        
        # Create a dictionary of professional profiles
        prof_dict = {
            prof.user_id: prof.as_dict()
            for prof in professionals
        }
        
        return jsonify({
            "requests": [req.as_dict() for req in requests],
            "professionals": prof_dict
        }), 200
    except Exception as e:
        return jsonify({"category": "danger", "message": str(e)}), 500

@admin_bp.route('/admin/export/<int:professional_id>', methods=['GET'])
@jwt_required()
@admin_required()
def export_service_requests(professional_id):
    """
    Export service requests for a professional
    ---
    tags:
      - Admin
    parameters:
      - name: professional_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Export task started successfully
      404:
        description: Professional not found
    """
    try:
        # Check if professional exists
        professional = ProfessionalProfile.query.filter_by(user_id=professional_id).first()
        if not professional:
            return jsonify({"category": "danger", "message": "Professional not found"}), 404

        # Get service requests for the professional
        requests = ServiceRequest.query.filter_by(professional_id=professional_id).all()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'service_requests_{professional_id}_{timestamp}.csv'
        filepath = os.path.join(REPORTS_DIR, filename)
        
        # Write to CSV
        with open(filepath, 'w') as f:
            # Write headers
            f.write('Request ID,Service Status,Date of Request,Date of Accept/Reject,Date of Completion,Remarks\n')
            
            # Write data
            for req in requests:
                f.write(f'{req.id},{req.service_status},{req.date_of_request},{req.date_of_accept_reject or ""},{req.date_of_completion or ""},{req.remarks or ""}\n')
        
        return jsonify({
            "category": "success",
            "message": "Export completed successfully",
            "filename": filename
        }), 200
        
    except Exception as e:
        return jsonify({"category": "danger", "message": str(e)}), 500

@admin_bp.route('/admin/reports/list', methods=['GET'])
@jwt_required()
@admin_required()
def list_reports():
    """
    List all available reports
    ---
    tags:
      - Admin
    responses:
      200:
        description: List of available reports
    """
    try:
        files = [f for f in os.listdir(REPORTS_DIR) if f.endswith('.csv')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(REPORTS_DIR, x)), reverse=True)
        return jsonify({"downloads": files}), 200
    except Exception as e:
        return jsonify({"category": "danger", "message": str(e)}), 500

@admin_bp.route('/admin/reports/download/<filename>', methods=['GET'])
@jwt_required()
@admin_required()
def download_report(filename):
    """
    Download a specific report
    ---
    tags:
      - Admin
    parameters:
      - name: filename
        in: path
        type: string
        required: true
    responses:
      200:
        description: Report file
      404:
        description: Report not found
    """
    try:
        return send_from_directory(REPORTS_DIR, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"category": "danger", "message": str(e)}), 404

@admin_bp.route('/admin/profile', methods=['GET'])
@jwt_required()
@admin_required()
def get_admin_profile():
    """
    Get admin profile information
    ---
    tags:
      - Admin
    responses:
      200:
        description: Admin profile data
      403:
        description: Not authorized as admin
    """
    try:
        user_id = get_jwt()['sub']
        admin = User.query.get(user_id)
        
        if not admin or admin.role != 'Admin':
            return jsonify({
                "category": "danger",
                "message": "Not authorized as admin"
            }), 403
            
        return jsonify({
            "category": "success",
            "data": {
                "id": admin.id,
                "username": admin.username,
                "role": admin.role,
                "date_created": admin.date_created.strftime('%Y-%m-%d %H:%M:%S') if admin.date_created else None
            },
            "message": "Profile data retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "category": "danger",
            "message": f"Error retrieving profile: {str(e)}"
        }), 500

@admin_bp.route('/admin/search', methods=['POST'])
@jwt_required()
@admin_required()
def search():
    """
    Search for customers, services, professionals, or service requests
    ---
    tags:
      - Admin
    parameters:
      - name: search_params
        in: body
        required: true
        schema:
          type: object
          properties:
            search_type:
              type: string
              enum: [customer, service, professional]
            search_text:
              type: string
    responses:
      200:
        description: Search results
      400:
        description: Invalid search parameters
    """
    try:
        data = request.get_json()
        search_type = data.get('search_type')
        search_text = data.get('search_text', '').strip()

        if not search_type:
            return jsonify({
                "category": "danger",
                "message": "Search type is required"
            }), 400

        response_data = {
            "customers": [],
            "professionals": [],
            "services": [],
            "service_requests": [],
            "service_type": {},
            "prof_dict": {},
            "cust_dict": {},
            "service_dict": {}
        }

        # Search based on type
        if search_type == 'service':
            services = Service.query.filter(
                or_(
                    Service.name.ilike(f'%{search_text}%'),
                    Service.service_type.ilike(f'%{search_text}%'),
                    Service.description.ilike(f'%{search_text}%')
                )
            ).all()
            response_data['services'] = [service.as_dict() for service in services]

        elif search_type == 'professional':
            professionals = (
                ProfessionalProfile.query
                .join(User, ProfessionalProfile.user_id == User.id)
                .filter(
                    or_(
                        ProfessionalProfile.full_name.ilike(f'%{search_text}%'),
                        ProfessionalProfile.service_type.ilike(f'%{search_text}%'),
                        User.username.ilike(f'%{search_text}%')
                    )
                )
                .all()
            )
            response_data['professionals'] = [prof.as_dict() for prof in professionals]

            # Get associated service requests
            prof_ids = [prof.user_id for prof in professionals]
            if prof_ids:
                service_requests = ServiceRequest.query.filter(
                    ServiceRequest.professional_id.in_(prof_ids)
                ).all()
                response_data['service_requests'] = [req.as_dict() for req in service_requests]

                # Get service types for professionals
                services = Service.query.all()
                response_data['service_type'] = {
                    service.id: service.as_dict()
                    for service in services
                }

        elif search_type == 'customer':
            customers = (
                CustomerProfile.query
                .join(User, CustomerProfile.user_id == User.id)
                .filter(
                    or_(
                        CustomerProfile.full_name.ilike(f'%{search_text}%'),
                        User.username.ilike(f'%{search_text}%'),
                        CustomerProfile.pin_code.ilike(f'%{search_text}%')
                    )
                )
                .all()
            )
            response_data['customers'] = [cust.as_dict() for cust in customers]

            # Get associated service requests
            cust_ids = [cust.user_id for cust in customers]
            if cust_ids:
                service_requests = ServiceRequest.query.filter(
                    ServiceRequest.customer_id.in_(cust_ids)
                ).all()
                response_data['service_requests'] = [req.as_dict() for req in service_requests]

                # Get customer details
                response_data['cust_dict'] = {
                    cust.user_id: cust.as_dict()
                    for cust in customers
                }

                # Get professional details for these requests
                prof_ids = set(req.professional_id for req in service_requests if req.professional_id)
                if prof_ids:
                    professionals = ProfessionalProfile.query.filter(
                        ProfessionalProfile.user_id.in_(prof_ids)
                    ).all()
                    response_data['prof_dict'] = {
                        prof.user_id: prof.as_dict()
                        for prof in professionals
                    }

                # Get service details
                service_ids = set(req.service_id for req in service_requests)
                if service_ids:
                    services = Service.query.filter(Service.id.in_(service_ids)).all()
                    response_data['service_dict'] = {
                        service.id: service.as_dict()
                        for service in services
                    }

        return jsonify({
            "category": "success",
            "message": "Search completed successfully",
            "data": response_data
        }), 200

    except Exception as e:
        return jsonify({
            "category": "danger",
            "message": f"Error performing search: {str(e)}"
        }), 500

@admin_bp.route('/admin/summary/reviews', methods=['GET'])
@jwt_required()
@admin_required()
def get_reviews_summary():
    """
    Get summary of professional reviews
    ---
    tags:
      - Admin
    responses:
      200:
        description: Reviews summary data
    """
    try:
        professionals = (
            ProfessionalProfile.query
            .with_entities(ProfessionalProfile.full_name, ProfessionalProfile.reviews)
            .filter(ProfessionalProfile.reviews > 0)
            .order_by(ProfessionalProfile.reviews.desc())
            .limit(5)
            .all()
        )
        
        return jsonify([{
            'full_name': prof.full_name,
            'reviews': prof.reviews
        } for prof in professionals]), 200
    except Exception as e:
        return jsonify({
            "category": "danger",
            "message": f"Error fetching reviews summary: {str(e)}"
        }), 500

@admin_bp.route('/admin/summary/ratings', methods=['GET'])
@jwt_required()
@admin_required()
def get_ratings_summary():
    """
    Get summary of customer ratings (1-5 stars)
    ---
    tags:
      - Admin
    responses:
      200:
        description: Ratings summary data
    """
    try:
        # Query to count ratings for each star level
        ratings_summary = db.session.query(
            Review.rating,
            func.count(Review.id).label('count')
        ).group_by(Review.rating).all()

        # Initialize counts dictionary
        counts = {
            'oneStar': 0,
            'twoStars': 0,
            'threeStars': 0,
            'fourStars': 0,
            'fiveStars': 0
        }

        # Map ratings to count
        rating_map = {
            1: 'oneStar',
            2: 'twoStars',
            3: 'threeStars',
            4: 'fourStars',
            5: 'fiveStars'
        }

        # Fill in actual counts
        for rating, count in ratings_summary:
            if rating in rating_map:
                counts[rating_map[rating]] = count

        return jsonify(counts), 200

    except Exception as e:
        print(f"Error fetching ratings summary: {str(e)}")
        return jsonify({
            "category": "danger",
            "message": f"Error fetching ratings summary: {str(e)}"
        }), 500

@admin_bp.route('/admin/summary/service_requests', methods=['GET'])
@jwt_required()
@admin_required()
def get_service_requests_summary():
    """
    Get summary of service requests for the last 7 days
    """
    try:
        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # Query to count service requests per day
        requests_by_date = db.session.query(
            func.strftime('%Y-%m-%d', ServiceRequest.date_of_request).label('date'),
            func.count(ServiceRequest.id).label('count')
        ).filter(
            ServiceRequest.date_of_request >= start_date,
            ServiceRequest.date_of_request <= end_date
        ).group_by(
            func.strftime('%Y-%m-%d', ServiceRequest.date_of_request)
        ).all()

        # Debugging: Check data types
        print("requests_by_date:", requests_by_date)
        print("Type of first date value:", type(requests_by_date[0][0]) if requests_by_date else "No data")

        # Convert results into a dictionary (No strftime needed since it's already a string)
        date_counts = {date: count for date, count in requests_by_date}

        # Generate all dates in range and fill in missing dates with 0
        all_dates = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            all_dates.append({
                'date': date_str,
                'count': date_counts.get(date_str, 0)
            })
            current_date += timedelta(days=1)

        return jsonify(all_dates), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/admin/service/<int:service_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_service(service_id):
    """
    Get a single service by ID
    ---
    tags:
      - Admin
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Service details
      404:
        description: Service not found
    """
    try:
        service = Service.query.get(service_id)
        if not service:
            return jsonify({"category": "danger", "message": "Service not found"}), 404
            
        return jsonify(service.as_dict()), 200
    except Exception as e:
        return jsonify({"category": "danger", "message": str(e)}), 500 