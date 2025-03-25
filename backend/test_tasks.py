from celery_worker import send_daily_reminders, generate_monthly_report

def test_tasks():
    print("Testing daily reminders...")
    result = send_daily_reminders.delay()
    print(f"Daily reminders task ID: {result.id}")
    
    print("\nTesting monthly report...")
    result = generate_monthly_report.delay()
    print(f"Monthly report task ID: {result.id}")

if __name__ == '__main__':
    test_tasks() 