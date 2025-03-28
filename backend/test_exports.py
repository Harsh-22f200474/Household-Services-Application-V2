#!/usr/bin/env python
"""
Test script to manually trigger the export Celery tasks.
This is useful for testing if the export functionality is 
working correctly without using the API.

Usage:
    python test_exports.py [professional_id]
    
    If professional_id is provided, it will test exporting data
    for that specific professional. Otherwise, it will export
    all service requests.
"""
import os
import sys
from app import create_app
from utils.celery_tasks import init_celery
from utils.export_tasks import register_export_tasks

# Get professional_id from command line args if provided
professional_id = int(sys.argv[1]) if len(sys.argv) > 1 else None

# Create the Flask app
app = create_app()

# Run the test within app context
with app.app_context():
    # Initialize Celery
    celery = init_celery(app)
    
    # Register export tasks
    export_tasks = register_export_tasks(celery)
    
    if professional_id:
        print(f"Testing export for professional ID: {professional_id}")
        
        # Manually run the professional export task and capture result
        try:
            # Get the task
            export_task = celery.tasks['export.service_professional']
            
            # Execute the task synchronously
            result = export_task.apply([professional_id])
            
            # Print the result
            print(f"Task completed with status: {result.status}")
            if result.successful():
                print("✅ Export task executed successfully!")
                print(f"Result: {result.result}")
            else:
                print("❌ Export task failed.")
                if result.traceback:
                    print("Error traceback:")
                    print(result.traceback)
        except Exception as e:
            print(f"❌ Error executing task: {e}")
    else:
        print("Testing export for all service requests")
        
        # Manually run the service requests export task and capture result
        try:
            # Get the task
            export_task = celery.tasks['export.service_requests']
            
            # Define some filters (or set to None for all requests)
            filters = {
                'status': 'completed'  # Example: only export completed requests
            }
            
            # Execute the task synchronously
            result = export_task.apply([filters])
            
            # Print the result
            print(f"Task completed with status: {result.status}")
            if result.successful():
                print("✅ Export task executed successfully!")
                print(f"Result: {result.result}")
            else:
                print("❌ Export task failed.")
                if result.traceback:
                    print("Error traceback:")
                    print(result.traceback)
        except Exception as e:
            print(f"❌ Error executing task: {e}") 