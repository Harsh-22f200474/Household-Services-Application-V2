#!/usr/bin/env python
"""
Test script to manually trigger the monthly activity report Celery task.
This is useful for testing if the monthly reports are being generated
and sent correctly without waiting for the scheduled time.

Usage:
    python test_reports.py
"""
import os
import sys
from app import create_app
from utils.celery_tasks import init_celery, generate_customer_report
from models import CustomerProfile

# Create the Flask app
app = create_app()

# Run the test within app context
with app.app_context():
    # Initialize Celery
    celery = init_celery(app)
    
    print("Testing monthly activity reports...")
    
    # Manually run the task and capture result
    try:
        # Get the task by name
        send_monthly_activity_report = celery.tasks['tasks.send_monthly_activity_report']
        
        # Execute the task synchronously
        result = send_monthly_activity_report.apply()
        
        # Print the result
        print(f"Task completed with status: {result.status}")
        print(f"Task result: {result.result}")
        
        if result.successful():
            print("✅ Monthly activity reports task executed successfully!")
            
            # Optionally, show a sample of what the reports contain
            print("\nSample report data:")
            customers = CustomerProfile.query.limit(1).all()
            if customers:
                sample_customer = customers[0]
                sample_report = generate_customer_report(sample_customer.user_id)
                print(f"Customer ID: {sample_customer.user_id}")
                print(f"Services used: {sample_report.get('services_used', 0)}")
                print(f"Total spent: ${sample_report.get('total_spent', 0):.2f}")
        else:
            print("❌ Monthly activity reports task failed.")
            if result.traceback:
                print("Error traceback:")
                print(result.traceback)
    except Exception as e:
        print(f"❌ Error executing task: {e}") 