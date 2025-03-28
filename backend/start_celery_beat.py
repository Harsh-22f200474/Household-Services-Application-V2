#!/usr/bin/env python
"""
Script to start Celery Beat for scheduled tasks.

This script creates a Flask app, initializes Celery with Beat scheduler,
and sets up periodic tasks for daily reminders and monthly reports.

Usage:
    python start_celery_beat.py

NOTE: This is for testing only. In production, you would use:
    celery -A app.celery beat --loglevel=info
"""
import os
import sys
import subprocess
from app import create_app
from celery.schedules import crontab

def setup_periodic_tasks(app):
    """
    Set up periodic tasks with Celery Beat
    """
    from utils.celery_tasks import init_celery
    
    celery = init_celery(app)
    
    # Configure the periodic tasks
    celery.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=9, minute=0),  # Every day at 9:00 AM
            'args': ()
        },
        'send-monthly-activity-report': {
            'task': 'tasks.send_monthly_activity_report',
            'schedule': crontab(day_of_month=1, hour=7, minute=0),  # First day of month at 7:00 AM
            'args': ()
        }
    }
    
    return celery

if __name__ == "__main__":
    # Create the Flask app
    app = create_app()
    
    # Set up the periodic tasks
    celery = setup_periodic_tasks(app)
    
    # Print information about the Beat scheduler
    print("Starting Celery Beat scheduler for periodic tasks...")
    print("Make sure Redis is running on localhost:6379")
    print("\nScheduled tasks:")
    print("  - Daily reminders: Every day at 9:00 AM")
    print("  - Monthly activity reports: First day of each month at 7:00 AM")
    
    # Build command to start Beat
    cmd = ["celery", 
           "-A", "utils.celery_tasks.celery", 
           "beat", 
           "--loglevel=info"]
    
    # Start the Beat scheduler
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting Celery Beat: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Celery Beat stopped by user.")
        sys.exit(0) 