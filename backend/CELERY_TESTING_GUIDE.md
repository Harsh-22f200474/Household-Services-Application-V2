# Celery Tasks Testing Guide

This guide helps you test the Celery tasks in your application, including daily reminders, monthly activity reports, and data exports.

## Prerequisites

1. Make sure Redis is installed and running on localhost:6379
2. Install all required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Testing Steps

### 1. Start Redis (if not already running)

**Windows:**
Download Redis for Windows from https://github.com/tporadowski/redis/releases and start it.

**Linux/Mac:**

```
redis-server
```

### 2. Start a Celery Worker

Run the included script to start a Celery worker:

```
python start_celery_worker.py
```

This will start a Celery worker that can process tasks. Keep this terminal window open.

### 3. Manual Testing of Tasks

#### 3.1. Test Daily Reminders

Open a new terminal window and run:

```
python test_reminders.py
```

This script will manually trigger the daily reminders task and show you the results. If successful, you should see:

- A success message in the console
- Google Chat notifications sent to the configured webhook URL

#### 3.2. Test Monthly Activity Reports

In a terminal, run:

```
python test_reports.py
```

This script will manually trigger the monthly activity reports task and show you the results. If successful, you should see:

- A success message in the console
- Email reports sent to the configured email address (check your email)
- Sample report data shown in the console

#### 3.3. Test Data Exports

To test the data export functionality, run:

```
python test_exports.py [professional_id]
```

If you provide a professional_id, it will test exporting data for that specific professional. Otherwise, it will export all service requests with a filter for completed status.

If successful, you should see:

- A success message in the console
- A CSV file generated in the reports directory
- Details about the result including the filename and path

#### 3.4. Test Asynchronous Export (API)

To test the asynchronous export functionality via the API, use the following endpoints:

1. Export Professional Data:

```
GET /admin/export/{professional_id}
```

2. Export Service Requests with Filters:

```
POST /admin/export-requests
Content-Type: application/json

{
  "status": "completed",
  "service_id": 1,
  "date_from": "2023-01-01",
  "date_to": "2023-12-31"
}
```

These endpoints will start tasks asynchronously and return task IDs. You should be able to observe the tasks being processed in the Celery worker terminal.

### 4. Testing Scheduled Tasks with Celery Beat

To test periodic scheduling of tasks (like running daily reminders automatically), you can use Celery Beat.

In a new terminal window, run:

```
python start_celery_beat.py
```

This will start the Celery Beat scheduler with the following schedule:

- Daily reminders: Every day at 9:00 AM
- Monthly activity reports: First day of each month at 7:00 AM

Note: Keep the Celery worker running in another terminal window, as Beat only schedules tasks but doesn't execute them.

#### Testing Tips for Scheduled Tasks:

1. For immediate testing, modify the schedule in `start_celery_beat.py` to run tasks sooner
2. Check the Celery worker terminal to see when tasks are being executed
3. Look for your reminder notifications and emails to confirm tasks are working

## Troubleshooting

### Common Issues:

1. **Redis Connection Error**:

   - Make sure Redis is running
   - Check the Redis connection settings in config.py

2. **Celery Task Not Found**:

   - Make sure the task name in your test script matches the task name defined in utils/celery_tasks.py

3. **Email Sending Failure**:

   - Check your email configuration in config.py
   - Make sure you can access the SMTP server

4. **Google Chat Webhook Issues**:

   - Verify the webhook URL is valid
   - Check for any network restrictions

5. **Celery Beat Schedule Not Working**:

   - Make sure both the Celery worker and Celery Beat are running
   - Verify task names match between your Beat schedule and task definitions
   - Check system time to ensure scheduled times are correct

6. **Export Tasks Failing**:
   - Check if the reports directory exists and is writable
   - Verify that you have valid data in your database
   - Check for database connection issues

If you encounter any other issues, check the error messages in the terminals where you're running the Celery worker and Beat scheduler.
