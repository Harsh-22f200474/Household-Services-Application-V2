from flask import current_app
from flask_mail import Message
from datetime import datetime

def send_email(subject, recipients, body=None, html=None):
    """
    Send an email using Flask-Mail
    """
    try:
        msg = Message(
            subject,
            recipients=recipients,
            body=body,
            html=html,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        current_app.extensions['mail'].send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_report_email(recipient, report_data, month=None):
    """
    Send a monthly report email
    """
    if month is None:
        month = datetime.now().strftime('%B %Y')
    
    subject = f"Monthly Activity Report - {month}"
    
    html_content = f"""
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
                <h2>Monthly Activity Report - {month}</h2>
                <div class="stat">
                    <strong>Services Used:</strong> {report_data.get('services_used', 0)}
                </div>
                <div class="stat">
                    <strong>Total Spent:</strong> ${report_data.get('total_spent', 0):.2f}
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_email(subject, [recipient], html=html_content) 