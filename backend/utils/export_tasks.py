"""
Celery tasks for exporting data to CSV files
"""
import os
import csv
from datetime import datetime
from models import db, ServiceRequest, ProfessionalProfile, CustomerProfile, User, Service
from sqlalchemy import func, and_, desc

# Constants
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

def register_export_tasks(celery_app):
    """
    Register export-related Celery tasks with the Celery app
    """
    @celery_app.task(name="export.service_professional")
    def export_service_professional(professional_id):
        """
        Export service professional data to CSV
        """
        # Check if professional exists
        professional = ProfessionalProfile.query.filter_by(user_id=professional_id).first()
        if not professional:
            return {"status": "error", "message": "Professional not found"}
            
        user = User.query.get(professional_id)
        if not user:
            return {"status": "error", "message": "User not found"}
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'professional_{professional_id}_{timestamp}.csv'
        filepath = os.path.join(REPORTS_DIR, filename)
        
        # Get service requests for the professional
        requests = ServiceRequest.query.filter_by(professional_id=professional_id).order_by(
            desc(ServiceRequest.date_of_request)
        ).all()
        
        # Get service types provided by professional
        service_types = professional.service_type.split(',') if professional.service_type else []
        
        # Write to CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write professional info
            writer.writerow(['Professional Information'])
            writer.writerow(['ID', 'Name', 'Username', 'Service Types', 'Date Joined'])
            writer.writerow([
                professional.user_id, 
                professional.full_name, 
                user.username,
                ', '.join(service_types),
                user.date_created.strftime('%Y-%m-%d') if user.date_created else 'Unknown'
            ])
            
            writer.writerow([])  # Empty row as separator
            
            # Write service request statistics
            total_requests = len(requests)
            completed_requests = sum(1 for req in requests if req.service_status == 'completed')
            accepted_rate = (completed_requests / total_requests * 100) if total_requests > 0 else 0
            
            writer.writerow(['Service Request Statistics'])
            writer.writerow(['Total Requests', 'Completed', 'Completion Rate'])
            writer.writerow([total_requests, completed_requests, f'{accepted_rate:.2f}%'])
            
            writer.writerow([])  # Empty row as separator
            
            # Write request details
            writer.writerow(['Service Requests'])
            writer.writerow(['Request ID', 'Service', 'Customer', 'Status', 'Request Date', 'Completion Date', 'Remarks'])
            
            for req in requests:
                service = Service.query.get(req.service_id)
                customer = CustomerProfile.query.filter_by(user_id=req.customer_id).first()
                
                writer.writerow([
                    req.id,
                    service.name if service else 'Unknown Service',
                    customer.full_name if customer else 'Unknown Customer',
                    req.service_status,
                    req.date_of_request.strftime('%Y-%m-%d') if req.date_of_request else 'Unknown',
                    req.date_of_completion.strftime('%Y-%m-%d') if req.date_of_completion else 'N/A',
                    req.remarks or 'No remarks'
                ])
                
        return {
            "status": "success", 
            "message": "Export completed", 
            "filename": filename,
            "path": filepath
        }
    
    @celery_app.task(name="export.service_requests")
    def export_service_requests(filters=None):
        """
        Export service requests to CSV, with optional filters
        
        filters: dict with optional keys:
            - status: Filter by service status
            - service_id: Filter by service type
            - date_from: Filter requests after this date
            - date_to: Filter requests before this date
        """
        # Build query with filters
        query = ServiceRequest.query
        
        if filters:
            if 'status' in filters and filters['status']:
                query = query.filter(ServiceRequest.service_status == filters['status'])
                
            if 'service_id' in filters and filters['service_id']:
                query = query.filter(ServiceRequest.service_id == filters['service_id'])
                
            if 'date_from' in filters and filters['date_from']:
                try:
                    date_from = datetime.strptime(filters['date_from'], '%Y-%m-%d')
                    query = query.filter(ServiceRequest.date_of_request >= date_from)
                except (ValueError, TypeError):
                    pass  # Invalid date format, ignore filter
                    
            if 'date_to' in filters and filters['date_to']:
                try:
                    date_to = datetime.strptime(filters['date_to'], '%Y-%m-%d')
                    query = query.filter(ServiceRequest.date_of_request <= date_to)
                except (ValueError, TypeError):
                    pass  # Invalid date format, ignore filter
        
        # Execute query and get results
        requests = query.order_by(desc(ServiceRequest.date_of_request)).all()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filter_suffix = '_filtered' if filters else ''
        filename = f'service_requests{filter_suffix}_{timestamp}.csv'
        filepath = os.path.join(REPORTS_DIR, filename)
        
        # Write to CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header and filter info
            writer.writerow(['Service Requests Export'])
            writer.writerow(['Generated on', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            
            if filters:
                writer.writerow(['Filters Applied'])
                for key, value in filters.items():
                    if value:
                        writer.writerow([key, value])
                        
            writer.writerow([])  # Empty row as separator
            
            # Write requests
            writer.writerow(['Request ID', 'Service', 'Professional', 'Customer', 'Status', 
                             'Request Date', 'Accept/Reject Date', 'Completion Date', 'Remarks'])
            
            for req in requests:
                service = Service.query.get(req.service_id)
                professional = ProfessionalProfile.query.filter_by(user_id=req.professional_id).first()
                customer = CustomerProfile.query.filter_by(user_id=req.customer_id).first()
                
                writer.writerow([
                    req.id,
                    service.name if service else 'Unknown Service',
                    professional.full_name if professional else 'Not Assigned',
                    customer.full_name if customer else 'Unknown Customer',
                    req.service_status,
                    req.date_of_request.strftime('%Y-%m-%d') if req.date_of_request else 'Unknown',
                    req.date_of_accept_reject.strftime('%Y-%m-%d') if req.date_of_accept_reject else 'N/A',
                    req.date_of_completion.strftime('%Y-%m-%d') if req.date_of_completion else 'N/A',
                    req.remarks or 'No remarks'
                ])
                
        return {
            "status": "success", 
            "message": "Export completed", 
            "filename": filename,
            "path": filepath,
            "request_count": len(requests)
        }
    
    return {
        "export_service_professional": export_service_professional,
        "export_service_requests": export_service_requests
    } 