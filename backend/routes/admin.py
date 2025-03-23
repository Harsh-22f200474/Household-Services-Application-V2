from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required
from models.models import User, Professional, Customer, Service

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def admin_dashboard():
    # Admin dashboard data
    total_users = User.query.count()
    total_professionals = Professional.query.count()
    pending_verifications = Professional.query.filter_by(is_verified=False).count()
    total_customers = Customer.query.count()
    
    return jsonify({
        'total_users': total_users,
        'total_professionals': total_professionals,
        'pending_verifications': pending_verifications,
        'total_customers': total_customers
    }), 200

@admin_bp.route('/professionals/pending', methods=['GET'])
@jwt_required()
@admin_required
def get_pending_professionals():
    professionals = Professional.query.filter_by(is_verified=False).all()
    return jsonify([{
        'id': prof.id,
        'user_id': prof.user_id,
        'service_type': prof.service_type,
        'experience': prof.experience
    } for prof in professionals]), 200

@admin_bp.route('/professionals/<int:prof_id>/verify', methods=['POST'])
@jwt_required()
@admin_required
def verify_professional(prof_id):
    professional = Professional.query.get_or_404(prof_id)
    professional.is_verified = True
    db.session.commit()
    return jsonify({"message": "Professional verified successfully"}), 200
