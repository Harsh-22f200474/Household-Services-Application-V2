import requests
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def send_chat_message(message, webhook_url):
    """
    Send a message to Google Chat using webhook
    
    Args:
        message (str): The message to send
        webhook_url (str): The Google Chat webhook URL
    """
    try:
        if not webhook_url:
            logger.warning("No webhook URL provided, skipping chat message")
            return False

        # Prepare the message payload
        payload = {
            "text": message
        }

        # Send the message
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes

        logger.info("Chat message sent successfully")
        return True

    except Exception as e:
        logger.error(f"Error sending chat message: {str(e)}")
        return False 