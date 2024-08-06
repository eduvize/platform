import boto3
from botocore.exceptions import ClientError

from config import get_aws_access_key, get_aws_secret_key, get_email_configuration_set, get_email_noreply_address, get_email_region

def send_email(to: str, subject: str, content: str):
    """
    Sends an email to a recipient using Amazon Simple Email Service (SES)

    Args:
        to (str): The recipient's email address
        subject (str): The email subject line
        content (str): The email body content
    """
    
    access_key = get_aws_access_key()
    secret_key = get_aws_secret_key()
    region = get_email_region()
    source_address = get_email_noreply_address()
    configuration_set = get_email_configuration_set()
    
    client = boto3.client(
        'ses', 
        region_name=region, 
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    to
                ]
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': content
                    }
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': subject
                }
            },
            Source=source_address,
            ConfigurationSetName=configuration_set
        )
    except ClientError as e:
        raise e
    
    return response['MessageId']