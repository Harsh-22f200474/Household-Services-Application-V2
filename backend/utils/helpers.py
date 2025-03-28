from flask import current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime

def format_datetime(dt):
    """Format datetime object to string"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def save_file(file, directory=None):
    """
    Save a file to the specified directory
    Returns the filename if successful, None if failed
    """
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_dir = directory or current_app.config['UPLOAD_FOLDER']
        
        # Create directory if it doesn't exist
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        try:
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            return filename
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    return None

def generate_report_html(report_data):
    """
    Generate HTML content for reports
    """
    return f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .report {{ padding: 20px; }}
                .stat {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="report">
                <h2>Activity Report</h2>
                <div class="stat">
                    <strong>Services Used:</strong> {report_data.get('services_used', 0)}
                </div>
                <div class="stat">
                    <strong>Total Spent:</strong> ${report_data.get('total_spent', 0):.2f}
                </div>
                <div class="stat">
                    <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </div>
        </body>
    </html>
    """ 