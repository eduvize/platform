import logging
from config import get_mailgun_key, get_email_noreply_address
import requests

logger = logging.getLogger(__name__)

def send_email(
    to: str, 
    subject: str, 
    content: str
):
    """
    Sends an email to a recipient using Amazon Simple Email Service (SES)

    Args:
        to (str): The recipient's email address
        subject (str): The email subject line
        content (str): The email body content
    """
    
    access_key = get_mailgun_key()
    source_address = get_email_noreply_address()
    
    response = requests.post(
        "https://api.mailgun.net/v3/mail.eduvize.dev/messages",
        auth=("api", access_key),
        data={
            "from": f"Eduvize <{source_address}>",
            "to": [to],
            "subject": subject,
            "html": content
        }
    )
    
    logger.info(f"Email sent to {to} with status code {response.status_code}")