from celery import Celery
from sqlalchemy import func
from models import db, CustomerProfile, ServiceRequest, ProfessionalProfile, Service
from datetime import datetime as DateTime
from .email import send_report_email
from .helpers import generate_report_html
import requests

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['RESULT_BACKEND'],
        broker=app.config['BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)
    celery.Task = ContextTask
    return celery

def init_celery(app):
    celery = make_celery(app)
    
    @celery.task(name="tasks.send_daily_reminders")
    def send_daily_reminders():
        pending_requests = (
            ServiceRequest.query.filter_by(service_status='requested')
            .join(ProfessionalProfile, ServiceRequest.professional_id == ProfessionalProfile.user_id)
            .add_columns(ProfessionalProfile.full_name)
            .all()
        )

        for service_request in pending_requests:
            professional_name = service_request.full_name
            chat_hook_url = 'https://chat.googleapis.com/v1/spaces/AAAAvRakfdA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=553wVqWmLUKCOHrlADdcoxnF4ThoR0MznD1WqQn3m18'
            
            message = {
                "text": f"Reminder: {professional_name}! You have pending service requests. Please visit or take action."
            }

            try:
                response = requests.post(chat_hook_url, json=message, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to send reminder to {professional_name}: {e}")
                continue
        return "Daily reminders sent successfully!"

    @celery.task(name="tasks.send_monthly_activity_report")
    def send_monthly_activity_report():
        customers = CustomerProfile.query.all()
        for customer in customers:
            report = generate_customer_report(customer.user_id)
            if 'error' not in report:
                send_report_email(
                    recipient='22f2000474@ds.study.iitm.ac.in',
                    report_data=report
                )
        return "Monthly activity reports sent successfully!"

    return celery

def generate_customer_report(customer_id):
    customer = CustomerProfile.query.filter_by(user_id=customer_id).first()
    if not customer:
        return {"error": "Customer not found"}

    report_data = (
        db.session.query(
            func.count(ServiceRequest.id).label("services_used"),
            func.sum(Service.price).label("total_spent")
        )
        .join(Service, ServiceRequest.service_id == Service.id)
        .filter(ServiceRequest.customer_id == customer_id)
        .filter(ServiceRequest.service_status == "completed")
        .one()
    )
    
    return {
        "services_used": report_data[0] or 0,
        "total_spent": float(report_data[1] or 0)
    } 