#!/usr/bin/env python
"""
Test script to manually trigger the daily reminders Celery task.
This is useful for testing if the task is working properly 
without waiting for the scheduled time.

Usage:
    python test_reminders.py
"""
import os
import sys
from app import create_app
from utils.celery_tasks import init_celery

# Create the Flask app
app = create_app()

# Run the test within app context
with app.app_context():
    # Initialize Celery
    celery = init_celery(app)
    
    print("Testing daily reminders...")
    
    # Manually run the task and capture result
    try:
        # Get the task by name
        send_daily_reminders = celery.tasks['tasks.send_daily_reminders']
        
        # Execute the task synchronously
        result = send_daily_reminders.apply()
        
        # Print the result
        print(f"Task completed with status: {result.status}")
        print(f"Task result: {result.result}")
        
        if result.successful():
            print("✅ Daily reminders task executed successfully!")
        else:
            print("❌ Daily reminders task failed.")
            if result.traceback:
                print("Error traceback:")
                print(result.traceback)
    except Exception as e:
        print(f"❌ Error executing task: {e}") 