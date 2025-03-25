from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models.models import User, ServiceRequest
from utils.email_utils import send_email
from utils.chat_utils import send_chat_message
import logging

# Initialize Celery
celery = Celery('tasks', broker='redis://localhost:6379/0')

# Configure Celery
celery.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_pool_restarts=True,  # Required for Windows
    broker_connection_retry_on_startup=True,  # Required for Windows
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task
def send_daily_reminders():
    """
    Daily task to send reminders to professionals about pending service requests
    """
    app = create_app()
    with app.app_context():
        try:
            # Get all professionals
            professionals = User.query.filter_by(role='professional').all()
            
            for professional in professionals:
                # Get pending service requests for this professional
                pending_requests = ServiceRequest.query.filter_by(
                    professional_id=professional.id,
                    status='requested'
                ).all()
                
                if pending_requests:
                    # Prepare reminder message
                    message = f"Hello {professional.name},\n\n"
                    message += "You have the following pending service requests:\n"
                    for request in pending_requests:
                        message += f"- Service ID: {request.id}, Customer: {request.customer.name}\n"
                    message += "\nPlease log in to your dashboard to accept or reject these requests."
                    
                    # Send reminder via email
                    send_email(
                        to_email=professional.email,
                        subject="Daily Service Request Reminder",
                        body=message
                    )
                    
                    # Send reminder via Google Chat (if configured)
                    send_chat_message(
                        message=message,
                        webhook_url=professional.chat_webhook_url  # You'll need to add this field to User model
                    )
                    
                    logger.info(f"Sent daily reminder to professional {professional.id}")
                    
        except Exception as e:
            logger.error(f"Error sending daily reminders: {str(e)}")
            raise

@celery.task
def generate_monthly_report():
    """
    Monthly task to generate and send activity reports to customers
    """
    app = create_app()
    with app.app_context():
        try:
            # Get all customers
            customers = User.query.filter_by(role='customer').all()
            
            for customer in customers:
                # Get the first day of the current month
                today = datetime.utcnow()
                first_day_of_month = today.replace(day=1)
                
                # Get all service requests for this customer in the current month
                monthly_requests = ServiceRequest.query.filter(
                    ServiceRequest.customer_id == customer.id,
                    ServiceRequest.date_of_request >= first_day_of_month
                ).all()
                
                if monthly_requests:
                    # Generate HTML report
                    html_content = f"""
                    <html>
                        <head>
                            <style>
                                body {{ font-family: Arial, sans-serif; }}
                                table {{ border-collapse: collapse; width: 100%; }}
                                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                th {{ background-color: #f2f2f2; }}
                            </style>
                        </head>
                        <body>
                            <h2>Monthly Activity Report - {today.strftime('%B %Y')}</h2>
                            <p>Dear {customer.name},</p>
                            <p>Here's your monthly service activity report:</p>
                            <table>
                                <tr>
                                    <th>Service ID</th>
                                    <th>Service Type</th>
                                    <th>Date Requested</th>
                                    <th>Date Completed</th>
                                    <th>Status</th>
                                    <th>Professional</th>
                                </tr>
                    """
                    
                    for request in monthly_requests:
                        html_content += f"""
                                <tr>
                                    <td>{request.id}</td>
                                    <td>{request.service.name}</td>
                                    <td>{request.date_of_request.strftime('%Y-%m-%d')}</td>
                                    <td>{request.date_of_completion.strftime('%Y-%m-%d') if request.date_of_completion else 'Pending'}</td>
                                    <td>{request.status}</td>
                                    <td>{request.professional.name if request.professional else 'Not Assigned'}</td>
                                </tr>
                        """
                    
                    html_content += """
                            </table>
                            <p>Thank you for using our services!</p>
                        </body>
                    </html>
                    """
                    
                    # Send email with the report
                    send_email(
                        to_email=customer.email,
                        subject=f"Monthly Activity Report - {today.strftime('%B %Y')}",
                        body=html_content,
                        is_html=True
                    )
                    
                    logger.info(f"Sent monthly report to customer {customer.id}")
                    
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            raise

# Schedule the tasks
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Schedule daily reminders at 8 PM UTC
    sender.add_periodic_task(
        crontab(hour=20, minute=0),
        send_daily_reminders.s(),
        name='daily-reminders'
    )
    
    # Schedule monthly report on the 1st of each month at 9 AM UTC
    sender.add_periodic_task(
        crontab(minute=0, hour=9, day_of_month='1'),  # Fixed crontab parameters
        generate_monthly_report.s(),
        name='monthly-report'
    )
