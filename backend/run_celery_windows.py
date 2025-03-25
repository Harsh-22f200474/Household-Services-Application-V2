import os
import sys
from celery_worker import celery

if __name__ == '__main__':
    # Set the pool to 'solo' for Windows
    os.environ.setdefault('CELERY_POOL', 'solo')
    
    # Start Celery worker
    argv = [
        'worker',
        '--pool=solo',  # Use solo pool for Windows
        '--loglevel=info',
        '--concurrency=1',  # Single worker for Windows
    ]
    
    celery.worker_main(argv) 