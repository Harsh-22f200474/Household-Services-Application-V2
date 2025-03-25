from flask import Blueprint, jsonify
from models.models import Service

services_bp = Blueprint('services', __name__)

@services_bp.route('/services/public', methods=['GET'])
def get_public_services():
    """Get all active services without requiring authentication"""
    try:
        services = Service.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': service.base_price
        } for service in services])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@services_bp.route('/services/public/<int:service_id>', methods=['GET'])
def get_service_by_id(service_id):
    """Get a single service by its ID"""
    try:
        service = Service.query.get(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        return jsonify({
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': service.base_price,
            'time_required': service.time_required,
            'is_active': service.is_active
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500