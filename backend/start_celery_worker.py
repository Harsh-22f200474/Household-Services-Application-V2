import subprocess
import sys

def start_celery():
    print("Starting Celery worker...")
    print("Make sure Redis is running on localhost:6379")
    
    try:
        # Use the correct module path
        result = subprocess.run([
            'celery',
            '-A',
            'utils.celery_tasks',  # Changed this line
            'worker',
            '--loglevel=info',
            '--pool=solo'  # Added for Windows compatibility
        ], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error starting Celery worker: {e}")
        return e.returncode

if __name__ == "__main__":
    sys.exit(start_celery()) 