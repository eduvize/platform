import logging
from config import get_mailgun_key, get_email_noreply_address
import aiohttp

logger = logging.getLogger(__name__)

async def send_email(
    to: str, 
    subject: str, 
    content: str
):
    """
    Sends an email to a recipient using Mailgun API asynchronously

    Args:
        to (str): The recipient's email address
        subject (str): The email subject line
        content (str): The email body content
    """
    
    access_key = get_mailgun_key()
    source_address = get_email_noreply_address()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.mailgun.net/v3/mail.eduvize.dev/messages",
            auth=aiohttp.BasicAuth("api", access_key),
            data={
                "from": f"Eduvize <{source_address}>",
                "to": [to],
                "subject": subject,
                "html": content
            }
        ) as response:
            status_code = response.status
    
    logger.info(f"Email sent to {to} with status code {status_code}")